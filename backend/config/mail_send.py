import smtplib
from email.message import EmailMessage

# STMP 서버의 url과 port 번호
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


def send_mail(receive_email, title, content):
    # 1. SMTP 서버 연결
    smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

    EMAIL_ADDR = "admin@wecoop.link"
    EMAIL_PASSWORD = "andzleldsjilswzl"

    # 2. SMTP 서버에 로그인
    smtp.login(EMAIL_ADDR, EMAIL_PASSWORD)

    message = EmailMessage()

    message.set_content(content)
    message["Subject"] = title
    message["From"] = EMAIL_ADDR  # 보내는 사람의 이메일 계정
    message["To"] = receive_email

    # 4. 서버로 메일 보내기
    smtp.send_message(message)

    # 5. 메일을 보내면 서버와의 연결 끊기
    smtp.quit()


import base64
import hmac
import time

import hashlib
import requests

NAVER_ACCESS_KEY = "g9Cz31zwENXZfcJXKt72"  # 인증키 관리 - Access Key ID
NAVER_SERVICE_ID = "ncp:sms:kr:296896132394:wecoop"  # 서비스 ID
NAVER_CALLING_NUMBER = "025670730"
NAVER_SERVICE_SECRET = "8Dtu5Qc68wJQSc3kXEsK4GVekokYqEZHlFSayVGs"  # 인증키 관리 - Secret Key


def make_signature(access_key, secret_key, timestamp, uri):
    secret_key = bytes(secret_key, "UTF-8")
    method = "POST"

    message = method + " " + uri + "\n" + timestamp + "\n" + access_key
    message = bytes(message, "UTF-8")
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return signingKey


# send_sms({message}, {phone_number})
def send_sms(phone_number, message):
    url = f"https://sens.apigw.ntruss.com"
    uri = f"/sms/v2/services/{NAVER_SERVICE_ID}/messages"
    access_key = NAVER_ACCESS_KEY
    secret_key = NAVER_SERVICE_SECRET
    timestamp = str(int(time.time() * 1000))

    body = {
        # "type": "SMS",
        "type": "LMS",
        # "contentType": "COMM",
        # "countryCode": "82",  # 82=한국
        "from": NAVER_CALLING_NUMBER,
        "content": f"[위쿱] {message}",
        "messages": [
            {
                "to": phone_number,
                # "content": message
            }
        ],
    }
    key = make_signature(access_key, secret_key, timestamp, uri)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "x-ncp-apigw-timestamp": timestamp,
        "x-ncp-iam-access-key": f"{NAVER_ACCESS_KEY}",
        "x-ncp-apigw-signature-v2": key,
    }
    response = requests.post(url + uri, json=body, headers=headers)
    return response
