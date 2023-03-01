import jwt
from datetime import datetime
from qwippit import db, login_manager
from flask_login import UserMixin
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    displayname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    # TODO: Followers and Following

    qwipps = db.relationship('Qwipp', backref='author', lazy=True)
    qwills = db.relationship('Qwill', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        reset_token = jwt.encode(
            {
                "user_id": self.id
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return reset_token

    @staticmethod
    def verify_reset_token(token):
        try:
            user_id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Qwipp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Qwipp('{self.content}', '{self.date_posted}')"


class Qwill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Qwipp('{self.content}', '{self.date_posted}')"