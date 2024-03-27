import smtplib
import ssl
import imaplib
import email
import openai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SpammedEmailResponder:
    def __init__(self, api_key, sender_email, password, sent_folder, inbox_folder, spam_folder):
        self.api_key = api_key
        self.sender_email = sender_email
        self.password = password
        self.sent_folder = sent_folder
        self.inbox_folder = inbox_folder
        self.spam_folder = spam_folder

    def login(self):
        context = ssl.create_default_context()
        self.smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
        self.smtp_server.login(self.sender_email, self.password)

        self.imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
        self.imap_server.login(self.sender_email, self.password)

    def move_emails_from_spam_to_inbox(self):
        self.imap_server.select(self.spam_folder)
        typ, data = self.imap_server.search(None, 'ALL')
        
        for num in data[0].split():
            self.imap_server.copy(num, self.inbox_folder)
            self.imap_server.store(num , '+FLAGS', '\\Deleted')
        self.imap_server.expunge()
        
    def reply_to_emails(self):
        self.imap_server.select(self.inbox_folder)
        typ, data = self.imap_server.search(None, 'UNSEEN')
        for num in data[0].split():
            typ, data = self.imap_server.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            sender = email_message['From']
            subject = email_message['Subject']
            body = self.get_email_body(email_message)
            new_body = self.ai_responder(body)
            self.send_email(subject=subject, body=new_body, receiver_email=sender)

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
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(str(body), "plain"))
        text = message.as_string()
        self.smtp_server.sendmail(self.sender_email, receiver_email, text)

    def ai_responder(self, message):
        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": "Reply to the following email message: " + str(message)
                    }
                ],
                temperature=0.8,
                max_tokens=200
            )
            return response.choices[0].message.content
        except openai.Error as e:
            print("Error:", e)
            return "Error: Maximum tokens exceeded. Please try again with a shorter input."

if __name__ == "__main__":
    new_api_key = ""
    sender_email = ""
    password = ""  
    new_sent_folder = 'SENT'
    new_inbox_folder = 'INBOX'
    new_spam_folder = '[Gmail]/Spam'

    gmail_bot = SpammedEmailResponder(
        new_api_key,
        sender_email,
        password,
        new_sent_folder,
        new_inbox_folder,
        new_spam_folder
    )

    gmail_bot.login()  
    gmail_bot.move_emails_from_spam_to_inbox() 
    gmail_bot.reply_to_emails()  
    print("Done")






























