from datetime import datetime, timezone, timedelta

from functools import wraps

from flask import make_response, request
from flask_cors import cross_origin
from flask_restx import Api, Resource, fields

import jwt

from email_scripts.gmail_automation_selenium import GmailAutomation
from email_scripts.respond_to_emails import MailResponderBot
from email_scripts.send_email import EmailGenerator
from email_scripts.spammed_email_responder import SpammedEmailResponder

from .models import db, User, JWTTokenBlocklist
from .config import BaseConfig

rest_api = Api(version="1.0", title="User API")


signup_model = rest_api.model('SignUpModel', {"username": fields.String(required=True, min_length=2, max_length=32),
                                              "email": fields.String(required=True, min_length=4, max_length=64),
                                              "password": fields.String(required=True, min_length=4, max_length=16)
                                              })

login_model = rest_api.model('LoginModel', {"email": fields.String(required=True, min_length=4, max_length=64),
                                            "password": fields.String(required=True, min_length=4, max_length=16)
                                            })

user_edit_model = rest_api.model('UserEditModel', {"userID": fields.String(required=True, min_length=1, max_length=32),
                                                   "username": fields.String(required=True, min_length=2, max_length=32),
                                                   "email": fields.String(required=True, min_length=4, max_length=64)
                                                   })

def token_required(f):

    @wraps(f)
    def decorator(*args, **kwargs):

        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return {"success": False, "msg": "Valid JWT token is missing"}, 400
        
        try:
            data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
            current_user = User.get_by_email(data["email"])

            if not current_user:
                return {"success": False,
                        "msg": "Sorry. Wrong auth token. This user does not exist."}, 400

            token_expired = db.session.query(JWTTokenBlocklist.id).filter_by(jwt_token=token).scalar()

            if token_expired is not None:
                return {"success": False, "msg": "Token revoked."}, 400

            if not current_user.check_jwt_auth_active():
                return {"success": False, "msg": "Token expired."}, 400

        except:
            return {"success": False, "msg": "Token is invalid"}, 400

        return f(current_user, *args, **kwargs)

    return decorator


@rest_api.route('/api/users/register')
class Register(Resource):
    @rest_api.expect(signup_model, validate=True)
    @token_required
    def post(self, current_user):
        print("Got it")
        token = request.headers["Authorization"].split(" ")[1]
        data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
        admin_email = data["email"]

        admin_user = User.get_by_email(admin_email)

        if not admin_user.is_admin:
            return {"success": False, "msg": "Only admins can add users."}, 403


        req_data = request.get_json()

        _username = req_data.get("username")
        _email = req_data.get("email")
        _password = req_data.get("password")

        user_exists = User.get_by_email(_email)
        if user_exists:
            return {"success": False,
                    "msg": "Email already taken"}, 400

        new_user = User(username=_username, email=_email)

        new_user.set_password(_password)
        new_user.save()

        return {"success": True,
                "userID": new_user.id,
                "msg": "The user was successfully registered"}, 200


@rest_api.route('/api/users/<int:id>')
class DeleteUser(Resource):
    @token_required
    def delete(self, _, id):
        print(id)
        token = request.headers["Authorization"].split(" ")[1]
        data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
        admin_email = data["email"]
        admin_user = User.get_by_email(admin_email)
        if not admin_user.is_admin:
            return {"success": False, "msg": "Only admins can delete users."}, 403
        
        user_to_delete = User.get_by_id(id)
        if not user_to_delete:
            return {"success": False, "msg": "User not found."}, 404
        user_to_delete.delete()
        return {"success": True, "msg": "User deleted successfully."}, 200


@rest_api.route('/api/users/login')
class Login(Resource):

    @rest_api.expect(login_model, validate=True)
    def post(self):
        print("GOt the reques")
        req_data = request.get_json()

        _email = req_data.get("email")
        _password = req_data.get("password")

        user_exists = User.get_by_email(_email)

        if not user_exists:
            return {"success": False,
                    "msg": "This email does not exist."}, 400

        if not user_exists.check_password(_password):
            return {"success": False,
                    "msg": "Wrong credentials."}, 400
        expiry_time = datetime.now() + timedelta(minutes=30)
        token = jwt.encode({'email': _email, 'exp': expiry_time}, BaseConfig.SECRET_KEY)

        user_exists.set_jwt_auth_active(True)
        user_exists.save()
        response = make_response({"success": True, "user": user_exists.toJSON()})
        response.set_cookie("access_token", token, httponly=True, expires=expiry_time, secure=True, samesite='None')
        
        return response
        

@rest_api.route('/api/users/edit')
class EditUser(Resource):
    """
       Edits User's username or password or both using 'user_edit_model' input
    """

    @rest_api.expect(user_edit_model)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _new_username = req_data.get("username")
        _new_email = req_data.get("email")

        if _new_username:
            self.update_username(_new_username)

        if _new_email:
            self.update_email(_new_email)

        self.save()

        return {"success": True}, 200
    
@rest_api.route('/api/users')
class GetAllUsers(Resource):
 
    @token_required
    def get(self, current_user):
        users = User.get_all()
        usersJson = [user.toJSON() for user in users]
        response =  make_response({"statusCode": 200, "users":usersJson })
        return response
    
@rest_api.route('/api/users/logout')
class LogoutUser(Resource):
    """
       Logs out User using 'logout_model' input
    """

    @token_required
    def post(self, current_user):

        _jwt_token = request.headers["Authorization"].split(" ")[1]

        jwt_block = JWTTokenBlocklist(jwt_token=_jwt_token, created_at=datetime.now(timezone.utc))
        jwt_block.save()

        self.set_jwt_auth_active(False)
        self.save()

        response = make_response({"success": True}, 200)
        response.delete_cookie("access_token")
        return response

        
@rest_api.route('/api/sendEmail')
class SendEmail(Resource):
    @token_required
    def post(self, current_user):
        try:
            data = request.get_json()
            prompt = data.get('message')
            from_email = data.get('senderEmail')
            to_email = data.get('receiverEmail')
            password = data.get('password')

            email_generator = EmailGenerator(BaseConfig.OPEN_API_KEY, BaseConfig.SENDGRID_API_KEY, prompt)

            subject, body = "", ""

            email_content = email_generator.generate_email_content(from_email, to_email)
            prompt_structure = "Subject:"
            subject_start_index = email_content.find(prompt_structure)
            if subject_start_index != -1:
                subject_end_index = email_content.find("\n\n", subject_start_index)
                subject = email_content[subject_start_index + len(prompt_structure):subject_end_index].strip()

                body_start_index = subject_end_index + 2  
                body = email_content[body_start_index:].strip()
            else:
                subject = "No subject"
                body = email_content.strip()
        
            response = email_generator.send_email(password,from_email, to_email, subject, body)

            if response["status"] == "success":
                return {"message": "Email sent successfully!",  "statusCode":200}, 200
            else:
                return {"message": "An error occurred while sending the email!"}, 500
            
        except Exception as e:
            return {"message": "An error occurred while sending the email!"}, 500


@rest_api.route('/api/respondToEmails')
class RespondToEmails(Resource):
    @token_required
    def post(self, current_user):
        try:
            data = request.get_json()
            sender_email = data.get('senderEmail')
            password = data.get('password')
            unread_messages = data.get('toWhom')
            print(unread_messages)
            sender = "Automatic Email Responder"
            api_role = "Email Responder"
            mail_host = "smtp.gmail.com"
            sent_folder = "SENT"
            inbox_folder = "INBOX"
            SMTP_SSL = 587
            IMAP_SSL = 993
            print("Before instance")
            mail_responder_bot = MailResponderBot(
                BaseConfig.OPEN_API_KEY,
                api_role,
                sender,
                mail_host,
                password,
                sender_email,
                sent_folder,
                inbox_folder,
                SMTP_SSL,
                IMAP_SSL
            )
            print("Instance created")
            num_emails_processed =  mail_responder_bot.reply_to_emails(unread_messages)
            print("done")
            message = f"Successfully responded to {num_emails_processed} emails!"
            return {"message": message,  "statusCode":200}, 200

        except Exception as e:
            return {"message": "An error occurred while responding to the emails!"}, 500
    
@rest_api.route('/api/respondToSpammedEmails')
class RespondToSpammedEmails(Resource):
    @token_required
    def post(self, current_user):
        try:
            data = request.get_json()
            sender_email = data.get('senderEmail')
            password = data.get('password')
            sent_folder = "SENT"
            inbox_folder = "INBOX"
            spam_folder = "[Gmail]/Spam"
            spammed_email_responder = SpammedEmailResponder(
                BaseConfig.OPEN_API_KEY,
                sender_email,
                password,
                sent_folder,
                inbox_folder,
                spam_folder,
            )
            
            spammed_email_responder.login()
            spammed_email_responder.move_emails_from_spam_to_inbox()
            spammed_email_responder.reply_to_emails()
            
            # gmail_automation = GmailAutomation(BaseConfig.OPEN_API_KEY, sender_email, password, "Yohannes")
            # gmail_automation.login()
            # gmail_automation.move_emails_from_spam_to_inbox()
            # gmail_automation.reply_to_emails()
            # gmail_automation.close_browser()

            message = "Successfully responded to spammed emails!"
            return {"message": message, "statusCode":200}, 200

        except Exception as e:
            return {"message": "An error occurred while responding to the spammed emails!"}, 500
