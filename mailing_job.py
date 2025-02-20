import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from retry import retry
from dotenv import load_dotenv
import os

# Get email configuration from .env
load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL')

# Get email addresses from mailing list
with open('mailing_list.txt', 'r') as file:
    TO_EMAILS = [line.strip() for line in file.readlines()]

# Functions
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = ', '.join(TO_EMAILS)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(FROM_EMAIL, TO_EMAILS, msg.as_string())
    server.quit()

@retry(tries=3, delay=40)  # Retry 3 times with a 2-minute delay
def fetch_data_from_api():
    print('Function fetching data from API()')
    url = 'https://kci-api-dxek.onrender.com/KC'
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    print(response)
    print(response.json())
    return response.json()

def job():
    print('Function job()')
    try:
        data = fetch_data_from_api()
        print(data)
        if data.get('isInjured'):
            print('is YES')
            answer = "YES"
            injury_type = data.get('InjuryType', 'unknown injury type')
            text = f"Kingsley Coman is currently injured. He suffers from {injury_type}."
        elif not data.get('isInjured'):
            print('is NO')
            answer = "NO"
            last_injury_date = data.get('lastInjuryDate', 'unknown date')
            text = f"Kingsley Coman is not currently injured. He has not been injured since {last_injury_date}."
        else:
            print('is else')
            answer = "UNKNOWN"
            text = "The injury status of Kingsley Coman is unknown."

        subject = 'Is Kingsley Coman injured today?'
        print(subject)
        body = f'{answer}! {text}'
        print(body)
        send_email(subject, body)
        print('Email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')

if __name__ == "__main__":
    job()