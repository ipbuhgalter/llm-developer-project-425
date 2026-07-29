import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
from dotenv import load_dotenv
import requests
import json
import time
import os

load_dotenv('../.env')

# === Настройки подключения ===
IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER") # Ваш email
IMAP_PASS = os.getenv("IMAP_PASS")    # Пароль приложения (не основной пароль!)

SMTP_HOST = os.getenv("SMTP_HOST")       # Хост SMTP
SMTP_USER = IMAP_USER
SMTP_PASS = IMAP_PASS

# Yandex REST API для генерации ответа
REST_API_URL = os.getenv("REST_API_URL")
FOLDER_ID = os.getenv("FOLDER_ID")         # Обязательно для Yandex REST API

# Получаем токен из метаданных
def get_iam_token():
    token_response = requests.get(
        "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token",
        headers={"Metadata-Flavor": "Google"}
    )
    iam_token = token_response.json()["access_token"]
    return iam_token

#IAM_TOKEN = get_iam_token()

# === Подключение к IMAP ===
def connect_imap():
    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(IMAP_USER, IMAP_PASS)
    return mail

# === Подключение к SMTP ===
def connect_smtp():
    server = smtplib.SMTP_SSL(SMTP_HOST, 465)
    server.login(SMTP_USER, SMTP_PASS)
    return server

# === Генерация ответа через Yandex Responses API ===
def generate_response(text):
    return "Спасибо за ваше сообщение."
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "folderId": FOLDER_ID,
        "text": text
    }
    try:
        response = requests.post(REST_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json().get("text", "Спасибо за ваше сообщение.")
    except Exception as e:
        print(f"Ошибка при генерации ответа: {e}")
        return "Спасибо за ваше сообщение."

# === Отправка ответа по SMTP ===
def send_reply(smtp_server, original_from, original_subject, reply_body):
    msg = MIMEMultipart()
    msg["From"] = IMAP_USER
    msg["To"] = original_from
    msg["Subject"] = f"Re: {original_subject}"

    # Добавляем тело письма
    msg.attach(MIMEText(reply_body, "plain", "utf-8"))

    try:
        smtp_server.send_message(msg)
        print(f"Ответ отправлен на {original_from}")
    except Exception as e:
        print(f"Ошибка отправки письма: {e}")

# === Основная логика ===
def process_unread_emails():
    mail = connect_imap()
    smtp_server = connect_smtp()

    # Выбираем папку INBOX
    mail.select("INBOX")

    # Ищем непрочитанные письма
    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    if not email_ids:
        print("Нет непрочитанных писем.")
        mail.close()
        mail.logout()
        smtp_server.quit()
        return

    for num in email_ids:
        try:
            # Получаем письмо
            status, msg_data = mail.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Извлекаем отправителя
            from_header = msg.get("From")
            sender_name, sender_email = parseaddr(from_header)

            # Извлекаем тему
            subject = msg.get("Subject", "Без темы")
            if subject.startswith("=?"):
                subject = email.header.decode_header(subject)[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

            # Извлекаем текст письма
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        charset = part.get_content_charset() or "utf-8"
                        body = part.get_payload(decode=True).decode(charset, errors="replace")
                        break
            else:
                charset = msg.get_content_charset() or "utf-8"
                body = msg.get_payload(decode=True).decode(charset, errors="replace")

            if not body.strip():
                body = "(Письмо не содержит текста)"

            # Генерируем ответ
            reply_text = generate_response(body)

            # Отправляем ответ
            send_reply(smtp_server, sender_email, subject, reply_text)

            # Помечаем письмо как прочитанное
            mail.store(num, "+FLAGS", r"\Seen")
            #mail.store(num, "-FLAGS", r"\Seen")
            print(f"Письмо от {sender_email} обработано и помечено как прочитанное.")

            # Задержка между письмами (чтобы не перегружать сервер)
            time.sleep(1)

        except Exception as e:
            print(f"Ошибка при обработке письма {num}: {e}")
            continue

    # Закрываем соединения
    mail.close()
    mail.logout()
    smtp_server.quit()

def handler(event, context):
    from lockbox import get_lockbox_secret
    IMAP_PASS = get_lockbox_secret(os.getenv("IMAP_PASS"), 'password')
    SMTP_PASS = IMAP_PASS
    process_unread_emails()
    return {
        'statusCode': 200,
        'body': 'Я тут запроцессил!',
    }

# === Запуск ===
if __name__ == "__main__":
    process_unread_emails()
