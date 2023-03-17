import jwt
from datetime import datetime
import time
from qwippit import db, login_manager
from flask_login import UserMixin
from flask import current_app



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Followers Table
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# Define the likes table
qwippLikes = db.Table('qwippLikes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('qwipp_id', db.Integer, db.ForeignKey('qwipp.id'), primary_key=True)
)

# Define the likes table
qwillLikes = db.Table('qwillLikes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('qwill_id', db.Integer, db.ForeignKey('qwill.id'), primary_key=True)
)

# Define the likes table
qwippViews = db.Table('qwippViews',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('qwipp_id', db.Integer, db.ForeignKey('qwipp.id'), primary_key=True),
    db.Column('views_count', db.Integer, default=1)
)

# Define the likes table
qwillViews = db.Table('qwillViews',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('qwill_id', db.Integer, db.ForeignKey('qwill.id'), primary_key=True),
    db.Column('views_count', db.Integer, default=1)
)

# Hashtags with Qwipps
qwippHashtag = db.Table('qwippHashtag',
    db.Column('qwipp_id', db.Integer, db.ForeignKey('qwipp.id'), primary_key=True),
    db.Column('hashtag_id', db.Integer, db.ForeignKey('hashtag.id'), primary_key=True),
)

# Hashtags with Qwills
qwillHashtag = db.Table('qwillHashtag',
    db.Column('qwill_id', db.Integer, db.ForeignKey('qwill.id'), primary_key=True),
    db.Column('hashtag_id', db.Integer, db.ForeignKey('hashtag.id'), primary_key=True),
)

# Replies on Qwipps
qwippReplies = db.Table('qwippReplies',
    db.Column('qwipp_id', db.Integer, db.ForeignKey('qwipp.id'), primary_key=True),
    db.Column('reply_id', db.Integer, db.ForeignKey('qwipp.id'), primary_key=True),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    displayname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    banner_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)

    emailverified = db.Column(db.Boolean(), nullable=False, default=False)

    followed = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id == id), secondaryjoin=(followers.c.followed_id == id), backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    viewed_qwipps = db.relationship('Qwipp', secondary='qwippViews', backref='hasViewed')
    viewed_qwills = db.relationship('Qwill', secondary='qwillViews', backref='hasViewed')

    liked_qwipps = db.relationship('Qwipp', secondary='qwippLikes', backref='hasLiked')
    liked_qwills = db.relationship('Qwill', secondary='qwillLikes', backref='hasLiked')

    qwipps = db.relationship('Qwipp', backref='author', lazy=True)
    qwills = db.relationship('Qwill', backref='author', lazy=True)

    # notifications
    like_notifications = db.Column(db.Boolean(), nullable=False, default=True)
    follow_notifications = db.Column(db.Boolean(), nullable=False, default=True)
    reply_notifications = db.Column(db.Boolean(), nullable=False, default=True)

    def get_reset_token(self, expires_sec=900):
        reset_token = jwt.encode(
            {
                "user_id": self.id,
                "timestamp": time.time()
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return reset_token

    @staticmethod
    def verify_token(token):
        try:
            user_id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_email_token(self, expires_sec=900):
        verify_email = jwt.encode(
            {
                "user_id": self.id,
                "timestamp": time.time()
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return verify_email

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    # Todo: Followed Qwipps and Qwills

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Qwipp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_edited = db.Column(db.DateTime)
    content = db.Column(db.Text(256), nullable=False)
    views = db.Column(db.Integer, nullable=False, default=0)
    likes = db.Column(db.Integer, nullable=False, default=0)
    is_reply = db.Column(db.Boolean(), nullable=False, default=False)
    qwipp_reply_id = db.Column(db.Integer)
    qwill_reply = db.Column(db.Integer, db.ForeignKey('qwill.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    replies = db.relationship('Qwipp', secondary=qwippReplies, primaryjoin=(qwippReplies.c.qwipp_id == id), secondaryjoin=(qwippReplies.c.reply_id == id), backref=db.backref('qwippReplies', lazy='dynamic'), lazy='dynamic')
    hashtags = db.relationship('Hashtag', secondary='qwippHashtag')

    def __repr__(self):
        return f"Qwipp('{self.content}', '{self.date_posted}')"


class Qwill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_edited = db.Column(db.DateTime)
    title = db.Column(db.Text(), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    views = db.Column(db.Integer, nullable=False, default=0)
    likes = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    replies = db.relationship('Qwipp', backref='qwill_reply', lazy=True)
    hashtags = db.relationship('Hashtag', secondary='qwillHashtag')

    def __repr__(self):
        return f"Qwill('{self.title}', '{self.content}', '{self.date_posted}')"


class Hashtag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return f"Hashtag('{self.content}')"
