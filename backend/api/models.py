from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.Text())
    is_admin = db.Column(db.Boolean(), default=False)
    jwt_auth_active = db.Column(db.Boolean())
    date_joined = db.Column(db.DateTime(), default=datetime.now())

    def __repr__(self):
        return f"{'Admin' if self.is_admin else 'User'} {self.username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_email(self, new_email):
        self.email = new_email

    def update_username(self, new_username):
        self.username = new_username

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_all(cls):
        return cls.query.all()

    def to_dict(self):
        return {
            '_id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin
        }
    def toJSON(self):
        return self.to_dict()


def seed_admin():
    existing_admin = User.query.filter_by(is_admin=True).first()
    if existing_admin:
        print("Admin user already exists.")
        return

    admin_username = "admin"
    admin_password = "admin123"  
    admin_email = "admin@example.com" 

    admin = User(username=admin_username, email=admin_email)
    admin.set_password(admin_password)
    admin.is_admin = True
    admin.save()

    print("Admin user seeded successfully.")



class JWTTokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jwt_token = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f"Expired Token: {self.jwt_token}"

    def save(self):
        db.session.add(self)
        db.session.commit()