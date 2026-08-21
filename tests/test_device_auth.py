import os
import tempfile
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="focus-auth-"))
os.environ["FOCUS_APP_DB_PATH"] = str(TMP / "app.db")
os.environ["FOCUS_USERNAME"] = "admin"
os.environ["FOCUS_PASSWORD"] = "adminpass1"
os.environ["FOCUS_MAIL_DEV_INBOX"] = "1"
os.environ["FOCUS_INVITE_CODES"] = "invite-one,invite-two"
os.environ["FOCUS_SESSION_SECRET"] = "test-session-secret"

from fastapi.testclient import TestClient

from backend.app import app
from backend.mailer import peek_dev_code


def fresh_client() -> TestClient:
    return TestClient(app)


def login(client: TestClient, username: str, password: str, extra_cookies: dict | None = None):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password, "remember": "1"},
        cookies=extra_cookies or {},
        follow_redirects=False,
    )


def test_existing_account_without_email_logs_in_directly():
    client = fresh_client()
    response = login(client, "admin", "adminpass1")
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "focus_session" in response.cookies
    assert "focus_login_challenge" not in response.cookies


def test_register_requires_email_and_new_device_asks_for_code():
    client = fresh_client()
    created = client.post(
        "/register",
        json={
            "username": "nowyuser",
            "password": "haslohaslo1",
            "invite_code": "invite-one",
            "email": "nowy@example.com",
        },
    )
    assert created.status_code == 201, created.text

    first = login(client, "nowyuser", "haslohaslo1")
    assert first.status_code == 303
    assert first.headers["location"] == "/login/verify"
    assert "focus_session" not in first.cookies
    challenge_cookie = first.cookies.get("focus_login_challenge")
    assert challenge_cookie

    wrong = client.post(
        "/auth/verify-device",
        data={"code": "000000"},
        cookies={"focus_login_challenge": challenge_cookie},
        follow_redirects=False,
    )
    assert wrong.status_code == 200
    assert "Niepoprawny kod" in wrong.text

    code = peek_dev_code("nowy@example.com")
    assert code and len(code) == 6

    verify_page = client.get(
        "/login/verify",
        cookies={"focus_login_challenge": challenge_cookie},
        follow_redirects=False,
    )
    assert verify_page.status_code == 200
    assert code in verify_page.text

    ok = client.post(
        "/auth/verify-device",
        data={"code": code},
        cookies={"focus_login_challenge": challenge_cookie},
        follow_redirects=False,
    )
    assert ok.status_code == 303
    assert ok.headers["location"] == "/"
    assert "focus_session" in ok.cookies
    device = ok.cookies.get("focus_device")
    assert device

    second_client = fresh_client()
    second = login(second_client, "nowyuser", "haslohaslo1", {"focus_device": device})
    assert second.status_code == 303
    assert second.headers["location"] == "/"
    assert "focus_session" in second.cookies


def test_unknown_device_is_challenged_again():
    client = fresh_client()
    created = client.post(
        "/register",
        json={
            "username": "drugiuser",
            "password": "haslohaslo2",
            "invite_code": "invite-two",
            "email": "drugi@example.com",
        },
    )
    assert created.status_code == 201, created.text
    first = login(client, "drugiuser", "haslohaslo2")
    assert first.headers["location"] == "/login/verify"


if __name__ == "__main__":
    test_existing_account_without_email_logs_in_directly()
    test_register_requires_email_and_new_device_asks_for_code()
    test_unknown_device_is_challenged_again()
    print("ok")
