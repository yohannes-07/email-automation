# from flask import Flask, request, jsonify
# from flask_cors import cross_origin, CORS
# from email_scripts.send_email import EmailGenerator
# from email_scripts.respond_to_emails import MailResponderBot
# from email_scripts.spammed_email_responder import SpammedEmailResponder
# from email_scripts.gmail_automation_selenium import GmailAutomation

# app = Flask(__name__)
# CORS(app)
# app.config.from_pyfile('settings.py')

# OPEN_API_KEY = app.config.get('OPEN_API_KEY')
# SEND_GRID_API_KEY = app.config.get('SENDGRID_API_KEY')

# @app.route('/sendEmail', methods=['POST'])
# @cross_origin()
# def sendEmail():
#     try:
#         data = request.get_json()
#         prompt = data.get('prompt')
#         from_email = data.get('from_email')
#         to_email = data.get('to_email')
#         password = data.get('password')

#         email_generator = EmailGenerator(OPEN_API_KEY, SEND_GRID_API_KEY, prompt)

#         subject, body = "", ""

#         email_content = email_generator.generate_email_content(from_email, to_email)

#         prompt_structure = "Subject:"
#         subject_start_index = email_content.find(prompt_structure)
#         if subject_start_index != -1:
#             subject_end_index = email_content.find("\n\n", subject_start_index)
#             subject = email_content[subject_start_index + len(prompt_structure):subject_end_index].strip()

#             body_start_index = subject_end_index + 2  
#             body = email_content[body_start_index:].strip()
#         else:
#             subject = "No subject"
#             body = email_content.strip()
    
#         status_code = email_generator.send_email(password,from_email, to_email, subject, body)
        
#         if status_code == 202:
#             return jsonify({"message": "Email sent successfully!"}), 200
#         else:
#             return jsonify({"message": "An error occurred while sending the email!"}), 500
        
#     except Exception as e:
#         return jsonify({"message": "An error occurred while sending the email!"}), 500


# @app.route('/respondToEmails', methods=['POST'])
# @cross_origin()
# def respondToEmails():
#     try:
#         data = request.json()
#         sender_email = data.get('sender_email')
#         password = data.get('password')
#         unread_messages = data.get('unread_messages')
#         sender = "Automatic Email Responder"
#         api_role = "Email Responder"
#         mail_host = "smtp.gmail.com"
#         sent_folder = "SENT"
#         inbox_folder = "INBOX"
#         SMTP_SSL = 465
#         IMAP_SSL = 993

#         mail_responder_bot = MailResponderBot(
#             OPEN_API_KEY,
#             api_role,
#             sender,
#             mail_host,
#             password,
#             sender_email,
#             sent_folder,
#             inbox_folder,
#             SMTP_SSL,
#             IMAP_SSL
#         )

#         num_emails_processed =  mail_responder_bot.reply_to_emails(unread_messages)
#         message = f"Successfully responded to {num_emails_processed} emails!"
#         return jsonify({"message": message}), 200

#     except Exception as e:
#         return jsonify({"message": "An error occurred while responding to the emails!"}), 500
    

# @app.route('/respondToSpammedEmails', methods=['POST'])
# @cross_origin()
# def respondToSpammedEmails():
#     try:
#         data = request.json()
#         sender_email = data.get('sender_email')
#         password = data.get('password')
#         sent_folder = "SENT"
#         inbox_folder = "INBOX"
#         spam_folder = "[Gmail]/Spam"

#         spammed_email_responder = SpammedEmailResponder(
#             OPEN_API_KEY,
#             sender_email,
#             password,
#             sent_folder,
#             inbox_folder,
#             spam_folder,
#         )
#         spammed_email_responder.login()
#         spammed_email_responder.move_emails_from_spam_to_inbox()
#         spammed_email_responder.reply_to_emails()

#         # gmail_automation = GmailAutomation(OPEN_API_KEY, sender_email, password, "Yohannes")
#         # gmail_automation.login()
#         # gmail_automation.move_emails_from_spam_to_inbox()
#         # gmail_automation.reply_to_emails()
#         # gmail_automation.close_browser()

#         message = "Successfully responded to spammed emails!"
#         return jsonify({"message": message}), 200

#     except Exception as e:
#         return jsonify({"message": "An error occurred while responding to the spammed emails!"}), 500
    

# if __name__ == '__main__':
#     app.run(debug=True)