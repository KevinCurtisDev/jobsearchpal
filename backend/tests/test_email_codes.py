from app.auth.email_codes import (
    MemoryEmailCodeStore,
    VerifyResult,
    generate_code,
    hash_secret,
    issue_code,
    verify_code,
)

PEPPER = "test-pepper"


def test_code_is_six_digits() -> None:
    for _ in range(200):
        code = generate_code()
        assert len(code) == 6 and code.isdigit()


def test_hash_depends_on_email_and_pepper() -> None:
    assert hash_secret("123456", "a@x.ie", PEPPER) != hash_secret("123456", "b@x.ie", PEPPER)
    assert hash_secret("123456", "a@x.ie", PEPPER) != hash_secret("123456", "a@x.ie", "other")
    assert hash_secret("123456", "A@X.ie ", PEPPER) == hash_secret("123456", "a@x.ie", PEPPER)


async def test_correct_code_verifies_once() -> None:
    store = MemoryEmailCodeStore()
    new = await issue_code(store, "aoife@example.ie", pepper=PEPPER, now=0, ttl_seconds=600)
    ok = await verify_code(
        store, "aoife@example.ie", new.code, pepper=PEPPER, now=10, max_attempts=5
    )
    again = await verify_code(
        store, "aoife@example.ie", new.code, pepper=PEPPER, now=11, max_attempts=5
    )
    assert ok is VerifyResult.OK
    assert again is VerifyResult.NOT_FOUND


async def test_expired_code_rejected() -> None:
    store = MemoryEmailCodeStore()
    new = await issue_code(store, "a@example.ie", pepper=PEPPER, now=0, ttl_seconds=600)
    assert (
        await verify_code(store, "a@example.ie", new.code, pepper=PEPPER, now=600, max_attempts=5)
        is VerifyResult.EXPIRED
    )


async def test_code_locks_after_max_attempts() -> None:
    store = MemoryEmailCodeStore()
    new = await issue_code(store, "a@example.ie", pepper=PEPPER, now=0, ttl_seconds=600)
    wrong = "000000" if new.code != "000000" else "111111"
    results = [
        await verify_code(store, "a@example.ie", wrong, pepper=PEPPER, now=1, max_attempts=5)
        for _ in range(5)
    ]
    assert results[:4] == [VerifyResult.INVALID] * 4
    assert results[4] is VerifyResult.LOCKED
    # Even the right code fails once locked.
    assert (
        await verify_code(store, "a@example.ie", new.code, pepper=PEPPER, now=2, max_attempts=5)
        is VerifyResult.LOCKED
    )


async def test_new_code_replaces_old() -> None:
    store = MemoryEmailCodeStore()
    first = await issue_code(store, "a@example.ie", pepper=PEPPER, now=0, ttl_seconds=600)
    second = await issue_code(store, "a@example.ie", pepper=PEPPER, now=1, ttl_seconds=600)
    if first.code != second.code:
        assert (
            await verify_code(
                store, "a@example.ie", first.code, pepper=PEPPER, now=2, max_attempts=5
            )
            is VerifyResult.INVALID
        )
    assert (
        await verify_code(store, "a@example.ie", second.code, pepper=PEPPER, now=3, max_attempts=5)
        is VerifyResult.OK
    )
