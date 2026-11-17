"""Email one-time sign-in codes.

Rules (docs/06-security.md §1.2):
- 6 digits from a CSPRNG; only an HMAC-SHA256 (with server pepper) is stored
- 10-minute expiry, one active code per email (a new code replaces the old one)
- 5 wrong attempts burn the code
- constant-time comparison
"""

import hashlib
import hmac
import json
import secrets
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Protocol

from redis.asyncio import Redis


def normalize_email(email: str) -> str:
    return email.strip().lower()


def generate_code() -> str:
    return f"{secrets.randbelow(10**6):06d}"


def generate_link_token() -> str:
    return secrets.token_urlsafe(32)


def hash_secret(value: str, email: str, pepper: str) -> str:
    message = f"{normalize_email(email)}:{value}".encode()
    return hmac.new(pepper.encode(), message, hashlib.sha256).hexdigest()


@dataclass
class IssuedCode:
    code_hash: str
    link_hash: str
    expires_at: float
    attempts: int = 0


class VerifyResult(StrEnum):
    OK = "ok"
    INVALID = "invalid"
    EXPIRED = "expired"
    LOCKED = "locked"
    NOT_FOUND = "not_found"


class EmailCodeStore(Protocol):
    async def save(self, email: str, issued: IssuedCode, ttl_seconds: int) -> None: ...
    async def get(self, email: str) -> IssuedCode | None: ...
    async def update(self, email: str, issued: IssuedCode) -> None: ...
    async def delete(self, email: str) -> None: ...


class MemoryEmailCodeStore:
    def __init__(self) -> None:
        self._data: dict[str, IssuedCode] = {}

    async def save(self, email: str, issued: IssuedCode, ttl_seconds: int) -> None:
        self._data[email] = issued

    async def get(self, email: str) -> IssuedCode | None:
        return self._data.get(email)

    async def update(self, email: str, issued: IssuedCode) -> None:
        self._data[email] = issued

    async def delete(self, email: str) -> None:
        self._data.pop(email, None)


class RedisEmailCodeStore:
    def __init__(self, redis: Redis, prefix: str = "authcode:") -> None:
        self._redis = redis
        self._prefix = prefix

    def _key(self, email: str) -> str:
        # Hash the email so raw addresses never sit in Redis keys.
        return self._prefix + hashlib.sha256(email.encode()).hexdigest()

    async def save(self, email: str, issued: IssuedCode, ttl_seconds: int) -> None:
        await self._redis.set(self._key(email), json.dumps(asdict(issued)), ex=ttl_seconds)

    async def get(self, email: str) -> IssuedCode | None:
        raw = await self._redis.get(self._key(email))
        return IssuedCode(**json.loads(raw)) if raw else None

    async def update(self, email: str, issued: IssuedCode) -> None:
        await self._redis.set(self._key(email), json.dumps(asdict(issued)), keepttl=True)

    async def delete(self, email: str) -> None:
        await self._redis.delete(self._key(email))


@dataclass(frozen=True)
class NewCode:
    code: str
    link_token: str


async def issue_code(
    store: EmailCodeStore, email: str, *, pepper: str, now: float, ttl_seconds: int
) -> NewCode:
    email_n = normalize_email(email)
    code = generate_code()
    token = generate_link_token()
    issued = IssuedCode(
        code_hash=hash_secret(code, email_n, pepper),
        link_hash=hash_secret(token, email_n, pepper),
        expires_at=now + ttl_seconds,
    )
    await store.save(email_n, issued, ttl_seconds)
    return NewCode(code=code, link_token=token)


async def verify_code(
    store: EmailCodeStore,
    email: str,
    code: str,
    *,
    pepper: str,
    now: float,
    max_attempts: int,
) -> VerifyResult:
    email_n = normalize_email(email)
    issued = await store.get(email_n)
    if issued is None:
        return VerifyResult.NOT_FOUND
    if now >= issued.expires_at:
        await store.delete(email_n)
        return VerifyResult.EXPIRED
    if issued.attempts >= max_attempts:
        return VerifyResult.LOCKED
    candidate = hash_secret(code.strip(), email_n, pepper)
    if hmac.compare_digest(candidate, issued.code_hash):
        await store.delete(email_n)  # single use
        return VerifyResult.OK
    issued.attempts += 1
    await store.update(email_n, issued)
    return VerifyResult.LOCKED if issued.attempts >= max_attempts else VerifyResult.INVALID
