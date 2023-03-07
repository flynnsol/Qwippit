from flask_login import current_user, login_user, logout_user
from sqlalchemy import func

from qwippit import bcrypt, db
from qwippit.models import User, Qwipp, Qwill
from flask import Blueprint, redirect, flash, url_for, render_template, request

from qwippit.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
from qwippit.users.utils import save_picture, save_banner

users = Blueprint('users', __name__)


@users.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, displayname=form.displayname.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to sign in.', 'success')
        return redirect(url_for('users.signin'))
    return render_template('users/signup.html', title='Sign Up', form=form)


@users.route("/signin", methods=['GET', 'POST'])
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
            flash('Sign In Unsuccessful. Please check email and password.', 'danger')
    return render_template('users/signin.html', title='Sign In', form=form)


@users.route("/signout")
def signout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/<string:username>", methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first_or_404()
    qwipps = Qwipp.query.filter_by(author=user)\
        .order_by(Qwipp.date_posted.desc()).all()
    qwills = Qwill.query.filter_by(author=user) \
        .order_by(Qwill.date_posted.desc()).all()
    if user.username == current_user.username:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            if form.banner.data:
                banner_file = save_banner(form.banner.data)
                current_user.banner_file = banner_file
            current_user.username = form.username.data
            current_user.displayname = form.displayname.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Account Information Updated.', 'success')
            return redirect(url_for('users.profile', username=current_user.username))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.displayname.data = current_user.displayname
            form.email.data = current_user.email
        return render_template('users/profile.html', qwipps=qwipps, qwills=qwills, user=user, title=user.displayname + " (@" + username + ")", form=form)
    return render_template('users/profile.html', qwipps=qwipps, qwills=qwills, user=user, title=user.displayname + " (@" + username + ")")


# Qwipps
@users.route("/<string:username>/qwipp/<int:qwipp_id>")
def qwipp(username, qwipp_id):
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first_or_404()
    qwipp = Qwipp.query.get_or_404(qwipp_id)
    return render_template('qwipps/qwipp.html', title=user.displayname + " (@" + username + ")", qwipp=qwipp, user=user)


@users.route("/<string:username>/qwill/<int:qwill_id>")
def qwill(username, qwill_id):
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first_or_404()
    qwill = Qwill.query.get_or_404(qwill_id)
    return render_template('qwills/qwill.html', title=user.displayname + " (@" + username + ")", qwill=qwill, user=user)


@users.route("/<string:username>/update")
def update_profile(username):
    return redirect(url_for('users.profile', username=username))
