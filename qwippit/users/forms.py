from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import PasswordField, SubmitField, StringField, FileField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from qwippit.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username (@)', validators=[DataRequired(), Length(min=2, max=16)])
    displayname = StringField('Display Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError('That username is in use. Please choose a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('That email is in use. Please choose a different email.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(8)])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Sign In')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is in use. Please choose a different username.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is in use. Please choose a different email.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Register an account first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(8), EqualTo('password')])

    submit = SubmitField('Reset Password')