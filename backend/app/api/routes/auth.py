"""Email-code sign-in (scaffold). Stage 1 adds sessions, magic-link sign-in, passkeys,
CSRF and the users table. See docs/06-security.md and docs/05-api-spec.md."""

import time
from typing import Literal

import structlog
from fastapi import APIRouter, Request, status
from pydantic import BaseModel, EmailStr, Field

from app.api.deps import (
    CodeStoreDep,
    EmailSenderDep,
    HttpClientDep,
    RateLimiterDep,
    SettingsDep,
    client_ip,
)
from app.auth import bot_protection as bots
from app.auth.email_codes import VerifyResult, issue_code, normalize_email, verify_code
from app.auth.email_sender import SignInEmail
from app.core.errors import ProblemError

router = APIRouter(prefix="/auth", tags=["auth"])
log = structlog.get_logger()


class EmailStartIn(BaseModel):
    email: EmailStr
    intent: Literal["signin", "signup"] = "signin"
    turnstile_token: str | None = Field(default=None, max_length=4096)
    website: str | None = Field(default=None, max_length=200, description="Honeypot: must be empty")
    form_started_at: int | None = Field(default=None, description="Epoch ms when the form rendered")


class EmailStartOut(BaseModel):
    sent: bool = True


class EmailVerifyIn(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\s*\d{6}\s*$")


class EmailVerifyOut(BaseModel):
    verified: bool


async def _limit(limiter: RateLimiterDep, key: str, limit: int, window: int) -> None:
    result = await limiter.hit(key, limit, window)
    if not result.allowed:
        raise ProblemError(
            429,
            "Too many attempts",
            f"Please wait {result.retry_after_seconds} seconds and try again.",
            headers={"Retry-After": str(result.retry_after_seconds)},
        )


@router.post("/email/start", status_code=status.HTTP_202_ACCEPTED, response_model=EmailStartOut)
async def email_start(
    body: EmailStartIn,
    request: Request,
    settings: SettingsDep,
    limiter: RateLimiterDep,
    store: CodeStoreDep,
    sender: EmailSenderDep,
    http: HttpClientDep,
) -> EmailStartOut:
    email = normalize_email(body.email)
    ip = client_ip(request)
    await _limit(limiter, f"email-start:ip:{ip}", 10, 3600)
    await _limit(limiter, f"email-start:email:{email}", 3, 900)

    # Silent rejections: bots get the same response as people, so they learn nothing.
    if bots.honeypot_triggered(body.website):
        log.info("signup_rejected", reason=bots.RejectReason.HONEYPOT)
        return EmailStartOut()
    if bots.submitted_too_fast(
        body.form_started_at, int(time.time() * 1000), settings.min_form_seconds
    ):
        log.info("signup_rejected", reason=bots.RejectReason.TOO_FAST)
        return EmailStartOut()

    if bots.is_disposable(email):
        raise ProblemError(
            422,
            "Please use a permanent email address",
            "Temporary email addresses can't be used to create an account.",
        )

    if settings.turnstile_enabled and settings.turnstile_secret_key is not None:
        result = await bots.verify_turnstile(
            http,
            token=body.turnstile_token,
            secret=settings.turnstile_secret_key.get_secret_value(),
            remote_ip=ip,
            expected_hostname=settings.turnstile_expected_hostname,
            expected_action=body.intent,
        )
        if not result.success:
            log.info("signup_rejected", reason=bots.RejectReason.TURNSTILE_FAILED)
            raise ProblemError(400, "We couldn't confirm you're human", "Please try again.")

    new = await issue_code(
        store,
        email,
        pepper=settings.auth_code_pepper.get_secret_value(),
        now=time.time(),
        ttl_seconds=settings.auth_code_ttl_seconds,
    )
    link = f"{settings.public_app_url}/sign-in/link#token={new.link_token}"
    await sender.send_sign_in(SignInEmail(to=email, code=new.code, link=link))
    # Same response whether or not an account exists (no account enumeration).
    return EmailStartOut()


@router.post("/email/verify", response_model=EmailVerifyOut)
async def email_verify(
    body: EmailVerifyIn,
    request: Request,
    settings: SettingsDep,
    limiter: RateLimiterDep,
    store: CodeStoreDep,
) -> EmailVerifyOut:
    await _limit(limiter, f"email-verify:ip:{client_ip(request)}", 10, 900)
    result = await verify_code(
        store,
        body.email,
        body.code,
        pepper=settings.auth_code_pepper.get_secret_value(),
        now=time.time(),
        max_attempts=settings.auth_code_max_attempts,
    )
    if result is VerifyResult.OK:
        # Stage 1: create or load the user, create a session, set the __Host- cookie.
        return EmailVerifyOut(verified=True)
    if result is VerifyResult.LOCKED:
        raise ProblemError(400, "Too many wrong codes", "Request a new code to try again.")
    if result is VerifyResult.EXPIRED:
        raise ProblemError(400, "That code has expired", "Request a new code.")
    raise ProblemError(400, "That code didn't work", "Check the code in your email and try again.")
