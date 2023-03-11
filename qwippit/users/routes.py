from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func

from qwippit import bcrypt, db
from qwippit.models import User, Qwipp, Qwill
from flask import Blueprint, redirect, flash, url_for, render_template, request, abort

from qwippit.qwipps.forms import QwippForm, QwillForm
from qwippit.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, UpdatePasswordForm, RequestResetForm, \
    ResetPasswordForm, RequestVerifyForm
from qwippit.users.utils import save_picture, save_banner, send_reset_email, send_verify_email

users = Blueprint('users', __name__)


# token blacklist
reset_blacklist = set()
verify_blacklist = set()

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
        send_verify_email(user)
        flash(f'Your account has been created! A link has been sent to verify your email address.', 'success')
        return redirect(url_for('users.signin'))
    return render_template('users/signup.html', title='Sign Up', form=form)


@users.route("/signin", methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == func.lower(form.email.data)).first_or_404()
        if user.emailverified:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Sign In Unsuccessful. Please check email and password.', 'danger')
        else:
            flash('Please verify your email address.', 'danger')
    return render_template('users/signin.html', title='Sign In', form=form)


@users.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/<string:username>")
def profile(username):
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first_or_404()
    qwipps = Qwipp.query.filter_by(author=user)\
        .order_by(Qwipp.date_posted.desc()).all()
    qwills = Qwill.query.filter_by(author=user) \
        .order_by(Qwill.date_posted.desc()).all()
    return render_template('users/profile.html', qwipps=qwipps, qwills=qwills, user=user, title=user.displayname + " (@" + username + ")")


# Qwipps
@users.route("/<string:username>/qwipp/<int:qwipp_id>")
def qwipp(username, qwipp_id):
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first_or_404()
    qwipp = Qwipp.query.get_or_404(qwipp_id)
    return render_template('qwipps/qwipp.html', title=user.displayname + " (@" + username + ")", qwipp=qwipp, user=user)


@users.route("/<string:username>/qwipp/<int:qwipp_id>/edit", methods=['GET', 'POST'])
@login_required
def update_qwipp(username, qwipp_id):
    qwipp = Qwipp.query.get_or_404(qwipp_id)
    if qwipp.author != current_user:
        abort(403)
    form = QwippForm()
    if form.validate_on_submit():
        qwipp.content = form.content.data
        db.session.commit()
        flash('Qwipp Updated!', 'success')
        return redirect(url_for('users.qwipp', username=username, qwipp_id=qwipp.id))
    elif request.method == 'GET':
        form.content.data = qwipp.content
    return render_template('qwipps/edit_qwipp.html', title=qwipp.author.displayname + " (@" + username + ")", qwipp=qwipp, qwipp_form=form)


@users.route('/<string:username>/qwipp/<int:qwipp_id>/delete', methods=['POST'])
@login_required
def delete_qwipp(username, qwipp_id):
    qwipp = Qwipp.query.get_or_404(qwipp_id)
    if qwipp.author != current_user:
        abort(403)
    db.session.delete(qwipp)
    db.session.commit()
    flash('Qwipp Deleted', 'success')
    return redirect(url_for('main.home'))


# Qwills
@users.route("/<string:username>/qwill/<int:qwill_id>")
def qwill(username, qwill_id):
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first_or_404()
    qwill = Qwill.query.get_or_404(qwill_id)
    return render_template('qwills/qwill.html', title=user.displayname + " (@" + username + ")", qwill=qwill, user=user)


@users.route("/<string:username>/qwill/<int:qwill_id>/edit", methods=['GET', 'POST'])
@login_required
def update_qwill(username, qwill_id):
    qwill = Qwill.query.get_or_404(qwill_id)
    if qwill.author != current_user:
        abort(403)
    form = QwillForm()
    if form.validate_on_submit():
        qwill.title = form.title.data
        qwill.content = form.content.data
        db.session.commit()
        flash('Qwill Updated!', 'success')
        return redirect(url_for('users.qwill', username=username, qwill_id=qwill.id))
    elif request.method == 'GET':
        form.title.data = qwill.title
        form.content.data = qwill.content
    return render_template('qwills/edit_qwill.html', title=qwill.author.displayname + " (@" + username + ")", qwill=qwill, qwill_form=form)


@users.route('/<string:username>/qwill/<int:qwill_id>/delete', methods=['POST'])
@login_required
def delete_qwill(username, qwill_id):
    qwill = Qwill.query.get_or_404(qwill_id)
    if qwill.author != current_user:
        abort(403)
    db.session.delete(qwill)
    db.session.commit()
    flash('Qwill Deleted', 'success')
    return redirect(url_for('main.home'))


@users.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
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
        return redirect(url_for('users.settings'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.displayname.data = current_user.displayname
        form.email.data = current_user.email
    return render_template('main/settings.html', title="Settings", form=form)


@users.route('/password', methods=['GET', 'POST'])
def change_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.currentpassword.data):
            current_user.password = hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.commit()
            flash(f'Your password has been changed.', 'success')
            return redirect(url_for('users.settings'))
        else:
            flash(f'Current password incorrect.', 'danger')
            return redirect(url_for('users.change_password'))
    return render_template('users/change_password.html', title="Change Password", form=form)

@users.route('/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Account Deleted.', 'success')
    return redirect(url_for('main.home'))


@users.route("/notifications")
@login_required
def notifications():
    return render_template('users/notifications.html', title="Notifications")


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Password reset instructions have been sent.', 'success')
        return redirect(url_for('users.signin'))
    return render_template('users/reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if token in reset_blacklist:
        flash('That token has already been used.', 'danger')
        return render_template('errors/400.html', title="Token Used (400)")

    user = User.verify_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated.', 'success')
        reset_blacklist.add(token)
        return redirect(url_for('users.signin'))
    return render_template('users/reset_token.html', title='Reset Password', form=form)


@users.route("/verify_email/<token>")
def verify_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if token in verify_blacklist:
        flash('That token has already been used.', 'danger')
        return render_template('errors/400.html', title="Token Used (400)")

    user = User.verify_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.signin'))
    else:
        flash('Email successfully verified! You can now Sign In!', 'success')
        user.emailverified = True
        db.session.commit()
        verify_blacklist.add(token)
        return redirect(url_for('users.signin'))


@users.route("/verify_email", methods=['GET', 'POST'])
def verify_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestVerifyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_verify_email(user)
        flash('Email Verification link has been sent.', 'success')
        return redirect(url_for('users.signin'))
    return render_template('users/verify_request.html', title='Verify Email', form=form)
