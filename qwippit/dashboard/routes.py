from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func

from qwippit import bcrypt
from qwippit.models import User
from qwippit.users.forms import LoginForm

dash = Blueprint('dash', __name__)


def getDashUsers():
    # TODO: Caching
    users = User.query.all()

    return users


@dash.route("/home", subdomain='dash')
def dash_home():
    if request.referrer:
        if current_user.is_authenticated:
            if len(current_user.roles) > 0:
                if current_user.roles[0].name == 'Admin':
                    return render_template('dash/home.html', title='Dashboard Home', users=getDashUsers())
            else:
                flash('You do not have access to that page.', 'danger')
                return redirect(url_for('dash.dash_redirect'))
        else:
            return redirect(url_for('dash.dash_signin'))
    else:
        return redirect(url_for('dash.dash_redirect'))


@dash.route("/", subdomain='dash')
def dash_redirect():
    logout_user()
    return redirect(url_for('dash.dash_signin'))


@dash.route("/signin", subdomain='dash', methods=['GET', 'POST'])
def dash_signin():
    if current_user.is_authenticated:
        return redirect(url_for('dash.dash_home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == func.lower(form.email.data)).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dash.dash_home'))
        else:
            flash('Sign In Unsuccessful. Please check email and password.', 'danger')
            return render_template('dash/signin.html', title='Dashboard Sign In', form=form)
    return render_template('dash/signin.html', title="Dashboard Sign In", form=form)