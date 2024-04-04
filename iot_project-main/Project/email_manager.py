import secrets
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string

class EmailManager:
    def __init__(self, sender, password, recipients):
        self.sender = sender
        self.password = password
        self.recipients = recipients

    def send_email(self, subject, body):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = self.recipients
        msg.attach(MIMEText(body))

        try:
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.login(self.sender, self.password)
            smtp_server.sendmail(self.sender, self.recipients, msg.as_string())
            smtp_server.quit()

            print('Email sent successfully.')
        except Exception as e:
            print(f'Error sending email: {e}')


    # GET the most RECENT email from recipients
    def read_recent_email_reply(self, unique_token, value):
        imap_ssl_host = 'imap.gmail.com'
        imap_ssl_port = 993
        imap = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
        imap.login(self.sender, self.password)
        imap.select("Inbox")

        _, msgnums = imap.search(None, f'FROM "{self.recipients}" UNSEEN')  # to only check email of a specific person

        if msgnums != [b'']:
            def check_for_re(email_num):
                email_num = str(email_num)[2: -1]

                print(email_num)
                try:
                    _, data = imap.fetch(email_num, '(RFC822)')
                except Exception as e:
                    print(f"Error during fetch: {e}")
                message = email.message_from_string(data[0][1].decode("utf-8"))

                subject_ = message.get('Subject')
                return subject_ == f'Re: {unique_token}'

            msgnum = None
            try:
                print(msgnums)
                msgnum = list(filter(check_for_re, msgnums[0].split()))[0]
            except Exception as e:
                print(e)

            data = None
            print(msgnum)
            try:
                _, data = imap.fetch(msgnum, '(RFC822)')
            except Exception as e:
                print(f"Error during fetch: {e}")

            message = None
            try:
                message = email.message_from_string(data[0][1].decode("utf-8"))
            except Exception as e:
                print(e)
            print(f"message: {message}")
            subject_ = None
            try:
                subject_ = message.get('Subject')
            except Exception as e:
                print(e)
            print(f"subject_: {subject_}")

            # Start of if statement
            print(unique_token)
            print(f'Re: {unique_token}')
            if subject_ == f'Re: {unique_token}':

                print('#-----------------------------------------#')
                print(f"Subject: {subject_}")
                print("Content:")

                print(f"message.walk(): {message.walk()}")
                for part in message.walk():
                    print(f"part: {part}")
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition'))

                    print(f"content_type: {content_type}")
                    print(f"content_disposition: {content_disposition}")
                    if content_type == "text/plain" and 'attachment' not in content_disposition:
                        msgbody = part.get_payload()
                        print(f"msgbody: {msgbody}")
                        first_line = msgbody.split('\n', 1)[0]
                        print(first_line)

                        imap.close()
                        return self.check_yes_response(first_line)

                # end of for loop
            # end of if statement

            print("Waiting...")
            imap.close()
        else:
            print('no new emails')
            imap.close()

    def generate_token(self, length):
        # combines all alphabet (uppercase and lowercase) with 0 to 9
        alphabet = string.ascii_letters + string.digits
        # secrets.choice() Return a randomly chosen element from a non-empty sequence.
        token = ''.join(secrets.choice(alphabet) for i in range(length))
        return token

    def check_yes_response(self, first_line):
        if str(first_line).strip().lower() == "yes":
            print("Fan will turn ON")
            return True
        else:
            print("Fan will stay OFF.")
            return False
