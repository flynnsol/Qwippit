from flask import Blueprint, render_template

hashtags = Blueprint('hashtags', __name__)



@hashtags.route("/#<string:hashtag>")
def qwipp(hashtag):
    return render_template('qwipps/qwipp.html', title="#" + hashtag)