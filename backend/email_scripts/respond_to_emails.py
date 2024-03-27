import smtplib, ssl
import time
import imaplib
import email
import openai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# import sendgrid
# from sendgrid.helpers.self.mail import Mail


class MailResponderBot:
    def __init__(self, api_key, api_role, sender, mail_host, password, sender_email, sent_folder, inbox_folder, IMAP_SSL, SMTP_SSL):
        self.api_key = api_key
        self.api_role = api_role
        self.sender = sender
        self.mail_host = mail_host
        self.password = password
        self.sender_email = sender_email
        self.sent_folder = sent_folder
        self.inbox_folder = inbox_folder
        self.IMAP_SSL = IMAP_SSL
        self.SMTP_SSL = SMTP_SSL
    
    def reply_to_emails(self, unread_messages: bool):
        num_emails_processed = 0
        print("starting...")
        context = ssl.create_default_context()
        self.smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
        self.smtp_server.login(self.sender_email, self.password)

        self.mail = imaplib.IMAP4_SSL(self.mail_host)
        print("self.mail created")
        self.mail.login(self.sender_email, self.password)
        print("logged in")
        self.mail.select(self.inbox_folder)
        print("selected Folder")
        status, messages = self.mail.search(None, unread_messages)
        message_ids = messages[0].split()
        print("lenght of message_ids", len(message_ids))

        for msg_id in message_ids:
            status, data = self.mail.fetch(msg_id, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)

            sender = email_message['From']
            subject = email_message['Subject']
            date = email_message['Date']

            body = self.get_email_body(email_message)
            new_body = self.ai_responder(body)
            self.send_email(subject=subject, body=new_body, receiver_email=sender)
            print("eziga")
            num_emails_processed += 1

        self.mail.logout()
        return num_emails_processed
    
    def get_email_body(self, email_message):
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content = part.get_content_type()
                disposition = str(part.get('Content-Disposition'))
                if content == 'text/plain' and 'attachment' not in disposition:
                    body = part.get_payload(decode=True) 
                    break
        else:
            body = email_message.get_payload(decode=True)

        return body
        
    def send_email(self, subject, body, receiver_email):
        # sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
        # message = Mail(
        #     from_email=self.sender_email,
        #     to_emails=receiver_email,
        #     subject=subject,
        #     html_content=body
        # )
        # try:
        #     response = sg.send(message)
        #     print(response.status_code)
        # except Exception as e:
        #     print("Error:", e)
        
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(str(body), "plain"))

        text = message.as_string()

        self.smtp_server.sendmail(self.sender_email, receiver_email, text)
        # context = ssl.create_default_context()
        
        # with smtplib.SMTP_SSL(self.mail_host, self.SMTP_SSL, context=context) as server:
        #     print("before login")
        #     server.login(self.sender_email, self.password)
        #     print("after login")
        #     server.sendmail(self.sender_email, receiver_email, text)
        #     print("sent")

        print("after sending")        
        # imap = imaplib.IMAP4_SSL(self.mail_host, self.IMAP_SSL)
        # imap.login(self.sender_email, self.password)
        # self.mail.append(self.sent_folder, '\\UnSeen', imaplib.Time2Internaldate(time.time()), text.encode('utf8'))
        # imap.logout()
    
    def ai_responder(self, message):
        
        client = openai.OpenAI(
            api_key=self.api_key
        )

        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            
            {
                "role": "user",
                "content": "Respond for the following email message" + str(message)
            }
        ],
        temperature=0.8,
        max_tokens=200
        )
       
        return response.choices[0].message.content
        

if __name__ == "__main__":
    new_api_key = ""
    new_mail_host = "smtp.gmail.com"
    new_password = "App Password" # If you are using gmail, you need to generate an app password(2f authentication)
    new_your_email = ""

    new_api_role = "Email Responder"

    new_subject = "New subject"
    new_sender = "Automatic Email Responder"    
    new_sent_folder = 'SENT'
    new_inbox_folder = 'INBOX'
    new_SMTP_SSL = 465
    new_IMAP_SSL = 993 
    
    mail_operator = MailResponderBot(
        new_api_key, 
        new_api_role, 
        new_sender, 
        new_mail_host, 
        new_password, 
        new_your_email, 
        new_sent_folder, 
        new_inbox_folder, 
        new_IMAP_SSL, 
        new_SMTP_SSL 
    )

    
    unread_messages = mail_operator.reply_to_emails(unread_messages=True)
    print("done")
