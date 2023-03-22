from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
from datetime import datetime

from qwippit import bcrypt, db
from qwippit.models import User, Qwipp, Qwill, qwippViews, qwillViews
from flask import Blueprint, redirect, flash, url_for, render_template, request, abort, jsonify

from qwippit.qwipps.forms import QwippForm, QwillForm
from qwippit.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, UpdatePasswordForm, RequestResetForm, \
    ResetPasswordForm, RequestVerifyForm
from qwippit.users.utils import save_picture, save_banner, send_reset_email, send_verify_email

users = Blueprint('users', __name__)


# token blacklist
reset_blacklist = set()
verify_blacklist = set()


@users.route("/check_auth")
def check_auth():
    if current_user.is_authenticated:
        response = {'authenticated': True}
    else:
        response = {'authenticated': False}
    return jsonify(response)

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
    if current_user.is_authenticated:
        if current_user.id != user.id:
            if qwipp not in current_user.viewed_qwipps:
                current_user.viewed_qwipps.append(qwipp)
                qwipp.views = qwipp.views + 1
            else:
                viewed_qwipp = db.session.query(qwippViews).filter_by(user_id=current_user.id, qwipp_id=qwipp.id).first()
                db.session.query(qwippViews).filter_by(user_id=current_user.id, qwipp_id=qwipp.id).update({"views_count": viewed_qwipp.views_count + 1})

            db.session.commit()

    reply_qwipp = Qwipp.query.get(qwipp.qwipp_reply_id)
    reply_qwill = Qwill.query.get(qwipp.qwill_reply_id)
    if reply_qwipp:
        return render_template('qwipps/qwipp.html', title=user.displayname + " (@" + username + ")", qwipp=qwipp, user=user, reply=reply_qwipp, isReplyToQwipp=True)
    elif reply_qwill:
        return render_template('qwipps/qwipp.html', title=user.displayname + " (@" + username + ")", qwipp=qwipp, user=user, reply=reply_qwill, isReplyToQwipp=False)
    else:
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
        qwipp.date_edited = datetime.utcnow()
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


@users.route('/<string:username>/qwipp/<int:qwipp_id>/like', methods=['POST'])
@login_required
def like_qwipp(username, qwipp_id):
    qwipp = Qwipp.query.get_or_404(qwipp_id)
    if qwipp.author == current_user:
        return jsonify({'likes': qwipp.likes})

    if qwipp in current_user.liked_qwipps:
        current_user.liked_qwipps.remove(qwipp)
        qwipp.likes = qwipp.likes - 1
    else:
        current_user.liked_qwipps.append(qwipp)
        qwipp.likes = qwipp.likes + 1

    db.session.commit()
    return jsonify({'likes': qwipp.likes})


@users.route("/<string:username>/qwipp/<int:qwipp_id>/reply", methods=['GET', 'POST'])
@login_required
def reply_qwipp(username, qwipp_id):
    qwipp = Qwipp.query.get_or_404(qwipp_id)
    form = QwippForm()
    if form.validate_on_submit():
        reply_qwipp = Qwipp(content=form.content.data, author=current_user, is_reply=True, qwipp_reply_id=qwipp.id)
        db.session.add(reply_qwipp)
        qwipp.replies.append(reply_qwipp)
        reply_qwipp.qwipp_reply.append(qwipp)
        db.session.commit()
        flash('Qwipp Created!', 'success')
        return redirect(url_for('users.qwipp', username=username, qwipp_id=reply_qwipp.id))
    return render_template('qwipps/reply.html', title=qwipp.author.displayname + " (@" + username + ") - Reply", qwipp=qwipp, isQwipp=True, qwipp_form=form)


# Qwills
@users.route("/<string:username>/qwill/<int:qwill_id>")
def qwill(username, qwill_id):
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first_or_404()
    qwill = Qwill.query.get_or_404(qwill_id)
    if current_user.is_authenticated:
        if current_user.id != user.id:
            if qwill not in current_user.viewed_qwills:
                current_user.viewed_qwills.append(qwill)
                qwill.views = qwill.views + 1
            else:
                viewed_qwill = db.session.query(qwillViews).filter_by(user_id=current_user.id, qwill_id=qwill.id).first()
                db.session.query(qwillViews).filter_by(user_id=current_user.id, qwill_id=qwill.id).update({"views_count": viewed_qwill.views_count + 1})
            db.session.commit()

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
        qwill.date_edited = datetime.utcnow()
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


@users.route('/<string:username>/qwill/<int:qwill_id>/like', methods=['POST'])
def like_qwill(username, qwill_id):
    qwill = Qwill.query.get_or_404(qwill_id)
    if current_user.is_authenticated:
        if qwill.author == current_user:
            return jsonify({'likes': qwill.likes})

        if qwill in current_user.liked_qwills:
            current_user.liked_qwills.remove(qwill)
            qwill.likes = qwill.likes - 1
        else:
            current_user.liked_qwills.append(qwill)
            qwill.likes = qwill.likes + 1

        db.session.commit()
        return jsonify({'likes': qwill.likes, 'authenticated': True})
    else:
        return jsonify({'likes': qwill.likes, 'authenticated': False})


@users.route("/<string:username>/qwill/<int:qwill_id>/reply", methods=['GET', 'POST'])
@login_required
def reply_qwill(username, qwill_id):
    qwill = Qwill.query.get_or_404(qwill_id)
    form = QwippForm()
    if form.validate_on_submit():
        reply_qwipp = Qwipp(content=form.content.data, author=current_user, is_reply=True, qwill_reply_id=qwill.id)
        db.session.add(reply_qwipp)
        qwill.replies.append(reply_qwipp)
        reply_qwipp.qwill_reply.append(qwill)
        db.session.commit()
        flash('Qwipp Created!', 'success')
        return redirect(url_for('users.qwipp', username=username, qwipp_id=reply_qwipp.id))
    return render_template('qwipps/reply.html', title=qwill.author.displayname + " (@" + username + ") - Reply", qwill=qwill, isQwipp=False, qwipp_form=form)


#End Qwills

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
