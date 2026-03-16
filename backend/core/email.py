import smtplib
from email.message import EmailMessage
from core.config import settings

def send_verification_email(to_email: str, code: str):
    msg = EmailMessage()
    msg['Subject'] = 'Подтверждение регистрации в ABox'
    msg['From'] = settings.yandex_smtp_user
    msg['To'] = to_email

    content = f"""Здравствуйте!

Ваш код подтверждения для ABox: {code}

Код действителен 10 минут.

С уважением,
Команда ABox"""
    msg.set_content(content)

    if settings.yandex_smtp_user and settings.yandex_smtp_password:
        try:
            with smtplib.SMTP_SSL(settings.yandex_smtp_host, settings.yandex_smtp_port) as server:
                server.login(settings.yandex_smtp_user, settings.yandex_smtp_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
            print(f"DEBUG Email: To={to_email}, Code={code}")
    else:
        print(f"DEBUG Email: To={to_email}, Code={code}")
