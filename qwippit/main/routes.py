from flask import Blueprint, request, render_template
from qwippit.qwipps.forms import QwippForm

main = Blueprint('main', __name__)

qwipps = [
    {
        'author': 'Flynn Sol',
        'content': 'Hello World, this is a content test. Please wrap this text around the div.',
        'date_posted': 'February 27, 2023'
    },
    {
        'author': 'John Brennan',
        'content': 'Hello World, this is a content test again. Please wrap this text around the div and hopefully it will wrap twice.',
        'date_posted': 'February 27, 2023'
    }
]


@main.route("/")
@main.route("/home")
def home():
    qwipp_form = QwippForm()
    return render_template('main/home.html', qwipps=qwipps, qwipp_form=qwipp_form, title='Home')