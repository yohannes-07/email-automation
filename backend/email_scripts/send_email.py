from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import sendgrid
from sendgrid.helpers.mail import Mail
from openai import OpenAI

class EmailGenerator:
    def __init__(self, openai_api_key, sendgrid_api_key, prompt):
        self.openai_api_key = openai_api_key
        self.sendgrid_api_key = sendgrid_api_key
        self.prompt = prompt
    
    def generate_email_content(self, from_email, to_email):
        client = OpenAI(api_key=self.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Use the following prompt to write email. Extract sender name from {from_email} and receiver name for dear[] from {to_email} \n" + str(self.prompt)
                }
            ],
            temperature=0.8,
            max_tokens=200
        )
        return response.choices[0].message.content
    
    def send_email(self, password, from_email, to_email, subject, body):
        message = MIMEMultipart()
        message["From"] = from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(str(body), "plain"))

        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com",465, context=context) as server:
            try:
                print("before login")
                server.login(from_email, password)
                print("after login")
                server.sendmail(from_email, to_email, text)
                print("sent")
                return {"status": "success", "message": "Email sent successfully!"}
            
            except Exception as e:
                return {"status": "error", "message": "An error occurred while sending the email."}


        # sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
        # email = Mail(
        #     from_email=from_email,
        #     to_emails=to_email,
        #     subject=subject,
        #     html_content=body
        # )
        # response = sg.send(email)
        # return response.status_code

# if __name__ == "__main__":
#     openai_api_key = ""
#     sendgrid_api_key = ""
#     prompt = "write an email to my boss about the new product launch."

#     email_generator = EmailGenerator(openai_api_key, sendgrid_api_key, prompt)

#     subject, body = "", ""

#     email_content = email_generator.generate_email_content()

#     prompt_structure = "Subject:"
#     subject_start_index = email_content.find(prompt_structure)
#     if subject_start_index != -1:
#         subject_end_index = email_content.find("\n\n", subject_start_index)
#         subject = email_content[subject_start_index + len(prompt_structure):subject_end_index].strip()

#         body_start_index = subject_end_index + 2  
#         body = email_content[body_start_index:].strip()
#     else:
#         subject = "No subject"
#         body = email_content.strip()

#     # email_generator.send_email('sender@gmail.com', 'targetemail@gmail.com', subject, body)
