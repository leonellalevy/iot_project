import secrets
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailManager:
    def __init__(self, sender, password, recipients):
        self.sender = sender
        self.password = password
        self.recipients = recipients

    def send_email(self, subject, body):
        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = self.recipients
            msg.attach(MIMEText(body))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(self.sender, self.password)
                smtp_server.sendmail(self.sender, self.recipients, msg.as_string())

            print('Email sent successfully.')
        except Exception as e:
            print(f'Error sending email: {e}')



    def read_email(self, unique_token, value):
        try:
            with imaplib.IMAP4_SSL('imap.gmail.com', 993) as imap:
                imap.login(self.sender, self.password)
                imap.select("Inbox")

                _, num_of_messages = imap.search(None, f'FROM "{self.recipients}" UNSEEN')

                if num_of_messages != [b'']:
                    for num in num_of_messages[0].split():
                        try:
                            _, data = imap.fetch(num, '(RFC822)')
                        except Exception as e:
                            print(f"Error while fetching messages: {e}")
                        message = email.message_from_bytes(data[0][1])
                        subject_ = message.get('Subject')
                        if subject_ == f'Re: {unique_token}':
                            for part in message.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get('Content-Disposition'))
                                if content_type == "text/plain" and 'attachment' not in content_disposition:
                                    message_text = part.get_payload()
                                    first_line = message_text.split('\n', 1)[0]
                                    #imap.close()
                                    return self.verify_answer(first_line)

                print("No relevant emails found.")
        except Exception as e:
            print(f'Error reading email: {e}')

    def generate_token(self, length):
        token = secrets.token_urlsafe(length)
        return token

    def verify_answer(self, first_line):
        response = str(first_line).strip().lower()
        print("Fan will turn ON" if response == "yes" else "Fan will stay OFF.")
        return response == "yes"
