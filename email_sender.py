import smtplib
import ssl

from settings import *

message = """Subject: Hi there again\n"""

context = ssl.create_default_context()


def send_email(body):
    with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(MAIL_FROM, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM, MAIL_TO, message + body)
