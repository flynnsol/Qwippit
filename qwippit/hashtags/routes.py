from flask import Blueprint, render_template

from qwippit.models import Hashtag

hashtags = Blueprint('hashtags', __name__)



@hashtags.route("/#<string:hashtagContent>")
def hashtag_feed(hashtagContent, hashtag_id):
    hashtag = Hashtag.query.get_or_404(hashtag_id)
    return render_template('hashtags/hashtag_feed.html', title="#" + hashtagContent, hashtag=hashtag)