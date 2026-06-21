import base64
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KEY_DIR = PROJECT_ROOT / "secrets"
PRIVATE_KEY_PATH = KEY_DIR / "vapid_private.pem"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def main() -> None:
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_raw = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )

    PRIVATE_KEY_PATH.write_bytes(private_pem)
    PRIVATE_KEY_PATH.chmod(0o600)

    print("Dodaj do .env:")
    print(f"VAPID_PUBLIC_KEY={_b64url(public_raw)}")
    print(f"VAPID_PRIVATE_KEY_FILE={PRIVATE_KEY_PATH.relative_to(PROJECT_ROOT)}")
    print("VAPID_SUBJECT=mailto:twoj-email@example.com")
    print("")
    print("Nie zmieniaj tych kluczy po wdrozeniu, bo stare subskrypcje przestana dzialac.")


if __name__ == "__main__":
    main()
