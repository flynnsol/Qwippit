from flask_login import current_user, login_user

from qwippit import bcrypt, db
from qwippit.models import User, Qwipp, Qwill
from flask import Blueprint, redirect, flash, url_for, render_template, request

from qwippit.users.forms import RegistrationForm, LoginForm

users = Blueprint('users', __name__)


@users.route("/u/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to login.', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/signup.html', title='Sign Up', form=form)


@users.route("/u/signin", methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('users/signin.html', title='Sign In', form=form)