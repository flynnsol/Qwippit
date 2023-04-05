from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import current_user
from sqlalchemy import func

from qwippit.qwipps.forms import QwippForm, QwillForm
from qwippit import db
from qwippit.models import Qwipp, Qwill, Hashtag, User

main = Blueprint('main', __name__)


def getQwipps():
    # TODO: The Algorithm
    qwipps = Qwipp.query.all()

    return qwipps


def getQwills():
    # TODO: The Algorithm
    qwills = Qwill.query.all()

    return qwills


def getHashtagQwipps(hashtag):
    # TODO: The Algorithm
    qwipps = Qwipp.query.filter(Qwipp.content.contains("#" + hashtag)).all()

    return qwipps


def getHashtagQwills(hashtag):
    # TODO: The Algorithm
    qwills = Qwill.query.filter(Qwill.content.contains("#" + hashtag)).all()

    return qwills


def getSearchQwipps(search_word):
    # TODO: The Algorithm
    qwipps = Qwipp.query.filter(Qwipp.content.contains(search_word)).all()

    return qwipps


def getSearchQwills(search_word):
    # TODO: The Algorithm
    qwills = Qwill.query.filter(Qwill.title.contains(search_word)).all()

    return qwills

def getSearchUsers(search_word):
    # TODO: The Algorithm
    users = User.query.filter(User.username.contains(search_word)).all()

    return users


def getSearchHashtags(search_word):
    # TODO: The Algorithm
    hashtags = Hashtag.query.filter(Hashtag.content.contains(search_word)).all()

    return hashtags



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
            hashtags = qwill_form.extract_hashtags()  # extract hashtags from the form
            for tag in hashtags:
                testhashtag = Hashtag.query.filter(func.lower(Hashtag.content) == func.lower(tag)).first()
                hashtag = Hashtag(content=tag)
                if testhashtag:
                    hashtag = testhashtag
                else:
                    db.session.add(hashtag)
                hashtag.qwills.append(qwill)
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
            hashtags = qwipp_form.extract_hashtags()  # extract hashtags from the form
            for tag in hashtags:
                testhashtag = Hashtag.query.filter(func.lower(Hashtag.content) == func.lower(tag)).first()
                hashtag = Hashtag(content=tag)
                if testhashtag:
                    hashtag = testhashtag
                else:
                    db.session.add(hashtag)
                hashtag.qwipps.append(qwipp)
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


@main.route("/h/<string:hashtag>")
def hashtagPosts(hashtag):
    qwipps = getHashtagQwipps(hashtag)
    qwills = getHashtagQwills(hashtag)
    return render_template('main/hashtag.html', title="#" + hashtag, qwipps=qwipps, qwills=qwills, hashtag=hashtag)


@main.route("/live-search", methods=['POST'])
def live_search():
    if request.method == 'POST':
        search_word = request.form['query']
        qwipps = getSearchQwipps(search_word)
        qwills = getSearchQwills(search_word)
        users = getSearchUsers(search_word)
        if search_word == '':
            qwipps = None
            qwills = None
            users = None
            return jsonify({'htmlresponse': render_template('main/empty.html')})
    return jsonify({'htmlresponse': render_template('main/livesearch.html', qwipps=qwipps, qwills=qwills, users=users, search_word=search_word)})
