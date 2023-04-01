from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user

from qwippit.qwipps.forms import QwippForm, QwillForm
from qwippit import db
from qwippit.models import Qwipp, Qwill

main = Blueprint('main', __name__)


def getQwipps():
    # TODO: The Algorithm
    qwipps = Qwipp.query.all()

    return qwipps


def getQwills():
    # TODO: The Algorithm
    qwills = Qwill.query.all()

    return qwills


@main.route("/", methods=['GET', 'POST'])
def index():
    return redirect(url_for('main.home'))

@main.route("/home", methods=['GET', 'POST'])
def home():
    qwipp_form = QwippForm()
    qwill_form = QwillForm()
    if qwill_form.validate_on_submit():
        if current_user.emailverified:
            qwill = Qwill(title=qwill_form.title.data, content=qwill_form.content.data, author=current_user)
            db.session.add(qwill)
            db.session.commit()
            flash('Qwill Created!', 'success')
            return redirect(url_for('users.qwill', username=current_user.username, qwill_id=qwill.id))
        else:
            flash('Please verify your email address.', 'danger')
            return redirect(url_for('main.home'))
    if qwipp_form.validate_on_submit():
        if current_user.emailverified:
            qwipp = Qwipp(content=qwipp_form.content.data, author=current_user)
            db.session.add(qwipp)
            db.session.commit()
            flash('Qwipp Created!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Please verify your email address.', 'danger')
            return redirect(url_for('main.home'))
    qwipps = getQwipps()
    qwills = getQwills()
    return render_template('main/home.html', qwipps=qwipps, qwills=qwills, qwipp_form=qwipp_form, qwill_form=qwill_form, title='Home')