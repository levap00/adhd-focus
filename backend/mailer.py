import os
import smtplib
from collections import deque
from email.message import EmailMessage
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

_TRUE = {"1", "true", "yes", "on"}
_DEV_INBOX: deque[dict[str, str]] = deque(maxlen=20)


class MailerError(Exception):
    pass


class MailerNotConfigured(MailerError):
    pass


def _env_flag(name: str, default: str = "0") -> bool:
    return (os.getenv(name, default) or default).strip().lower() in _TRUE


def dev_inbox_enabled() -> bool:
    return _env_flag("FOCUS_MAIL_DEV_INBOX")


def is_configured() -> bool:
    if dev_inbox_enabled():
        return True
    return bool((os.getenv("FOCUS_SMTP_HOST") or "").strip())


def peek_dev_code(email: str = "") -> str:
    if not dev_inbox_enabled():
        return ""
    needle = (email or "").strip().lower()
    for item in reversed(_DEV_INBOX):
        if not needle or item.get("to", "").lower() == needle:
            return item.get("code", "")
    return ""


def _from_address() -> str:
    return (os.getenv("FOCUS_SMTP_FROM") or os.getenv("FOCUS_SMTP_USER") or "focus@localhost").strip()


def _build_message(to_email: str, subject: str, text_body: str, html_body: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = _from_address()
    message["To"] = to_email
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")
    return message


def _send_smtp(message: EmailMessage) -> None:
    host = (os.getenv("FOCUS_SMTP_HOST") or "").strip()
    if not host:
        raise MailerNotConfigured("Brak FOCUS_SMTP_HOST.")

    port = int(os.getenv("FOCUS_SMTP_PORT", "587") or "587")
    username = (os.getenv("FOCUS_SMTP_USER") or "").strip()
    password = os.getenv("FOCUS_SMTP_PASSWORD") or ""
    use_ssl = _env_flag("FOCUS_SMTP_SSL")
    use_starttls = _env_flag("FOCUS_SMTP_STARTTLS", "1")

    try:
        if use_ssl:
            smtp: smtplib.SMTP = smtplib.SMTP_SSL(host, port, timeout=20)
        else:
            smtp = smtplib.SMTP(host, port, timeout=20)
        with smtp:
            smtp.ehlo()
            if use_starttls and not use_ssl:
                smtp.starttls()
                smtp.ehlo()
            if username:
                smtp.login(username, password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise MailerError("Nie udalo sie wyslac wiadomosci e-mail.") from exc


def send_login_code(to_email: str, code: str, username: str, purpose: str = "login_device") -> None:
    clean_email = (to_email or "").strip()
    clean_code = (code or "").strip()
    if not clean_email or not clean_code:
        raise MailerError("Brak adresu albo kodu.")

    if purpose == "verify_email":
        subject = "Kod potwierdzenia e-mail | ADHD Focus OS"
        intro = "Potwierdz adres e-mail kodem ponizej."
    else:
        subject = "Kod logowania | ADHD Focus OS"
        intro = "Nowe urzadzenie chce zalogowac sie na Twoje konto."

    text_body = (
        f"Czesc {username},\n\n"
        f"{intro}\n\n"
        f"Kod: {clean_code}\n\n"
        "Kod jest wazny 10 minut. Jesli to nie Ty, zignoruj wiadomosc i zmien haslo.\n"
    )
    html_body = f"""
    <div style="font-family: system-ui, sans-serif; color: #0f172a; line-height: 1.5;">
      <p>Czesc {username},</p>
      <p>{intro}</p>
      <p style="font-size: 28px; font-weight: 800; letter-spacing: 0.18em; margin: 24px 0;">{clean_code}</p>
      <p>Kod jest wazny 10 minut. Jesli to nie Ty, zignoruj wiadomosc i zmien haslo.</p>
    </div>
    """

    if dev_inbox_enabled():
        _DEV_INBOX.append({"to": clean_email, "code": clean_code, "purpose": purpose, "username": username})
        if not (os.getenv("FOCUS_SMTP_HOST") or "").strip():
            return

    if not (os.getenv("FOCUS_SMTP_HOST") or "").strip():
        raise MailerNotConfigured("Wysylka e-mail nie jest skonfigurowana.")

    _send_smtp(_build_message(clean_email, subject, text_body, html_body))


def last_dev_message() -> Optional[dict[str, str]]:
    if not dev_inbox_enabled() or not _DEV_INBOX:
        return None
    return dict(_DEV_INBOX[-1])
