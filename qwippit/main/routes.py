from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import current_user

from qwippit.qwipps.forms import QwippForm
from qwippit import db
from qwippit.models import Qwipp

main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    qwipp_form = QwippForm()
    if qwipp_form.validate_on_submit():
        qwipp = Qwipp(content=qwipp_form.content.data, author=current_user)
        db.session.add(qwipp)
        db.session.commit()
        return redirect(url_for('main.home'))
    qwipps = Qwipp.query.all()
    return render_template('main/home.html', qwipps=qwipps, qwipp_form=qwipp_form, title='Home')