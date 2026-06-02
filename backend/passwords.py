from passlib.context import CryptContext


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=True)


def get_password_hash(password: str) -> str:
    return password_context.hash(password or "")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return password_context.verify(plain_password or "", hashed_password)
    except (TypeError, ValueError):
        return False
