from dotenv import load_dotenv
import os
from email.message import EmailMessage
from email.utils import formataddr
import datetime
import smtplib



def send_email(message, subject, destination, html = False, replyto = False):
    server = smtplib.SMTP('smtp.eu.mailgun.org', 587)
    server.starttls()
    load_dotenv()
    password = os.getenv('EMAIL_PASSWORD')
    username = os.getenv('EMAIL_USERNAME')
    server.login(username, password)
    msg = EmailMessage()
    if html:
        msg.set_content(message, subtype='html')
    else:
        msg.set_content(message)

    msg['Subject'] = subject
    msg['From'] = formataddr(('BotPanda', 'bot@mail.evilpanda.live'))
    msg['To'] = destination
    if replyto:
        msg['Reply-To'] = replyto
    server.send_message(msg)


async def send(content, name, email, autoresponse):
    send_email(content, f"BotPanda: New message from '{name}' {str(datetime.datetime.now().strftime('%Y-%m-%d'))}", destination="williamadamsat24@gmail.com", replyto=email)
    send_email(autoresponse, f"BotPanda: Thanks for contacting Evilpanda", destination=email)


async def process_message(name, email, message):
    if await check_email(email):
        content = f"New message!\n\nName: {name}\nEmail: {email}\n\nMessage:\n{message}\n\n\nThis message was sent automatically by BotPanda."
        autoresponse = f"Hi {name},\n\nThank you for contacting EvilPanda. I will hopefully get back to you soon.\n\n\nName: {name}\nEmail: {email}\nMessage:\n{message}\n\n\nThis message was sent automatically by BotPanda. Do not reply to this email."
        await send(content, name, email, autoresponse)
        return 'success'
    else:
        return 'invalid email'



async def check_email(email):
    if '@' in email and '.' in email:
        return True