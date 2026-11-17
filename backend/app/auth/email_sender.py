"""Transactional email. SMTP (Mailpit) in development; Postmark or SES adapters in Stage 1."""

import smtplib
from dataclasses import dataclass, field
from email.message import EmailMessage
from typing import Protocol

from starlette.concurrency import run_in_threadpool


@dataclass(frozen=True)
class SignInEmail:
    to: str
    code: str
    link: str


class EmailSender(Protocol):
    async def send_sign_in(self, message: SignInEmail) -> None: ...


def render_sign_in(message: SignInEmail, app_name: str, site: str) -> tuple[str, str]:
    subject = f"Your {app_name} sign-in code: {message.code}"
    body = (
        f"Your sign-in code is {message.code}\n\n"
        f"It expires in 10 minutes. Or open this link on the same device:\n{message.link}\n\n"
        f"Only enter this code on {site}. We will never ask you for it by phone, chat or email.\n"
        "If you didn't ask to sign in, you can ignore this email.\n"
    )
    return subject, body


@dataclass
class MemoryEmailSender:
    """Captures emails for tests."""

    sent: list[SignInEmail] = field(default_factory=list)

    async def send_sign_in(self, message: SignInEmail) -> None:
        self.sent.append(message)


class SmtpEmailSender:
    def __init__(self, host: str, port: int, sender: str, app_name: str, site: str) -> None:
        self.host, self.port, self.sender = host, port, sender
        self.app_name, self.site = app_name, site

    def _send(self, message: SignInEmail) -> None:
        subject, body = render_sign_in(message, self.app_name, self.site)
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = self.sender, message.to, subject
        msg.set_content(body)
        with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
            smtp.send_message(msg)

    async def send_sign_in(self, message: SignInEmail) -> None:
        await run_in_threadpool(self._send, message)
