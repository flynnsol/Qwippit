from flask import Blueprint, request, render_template

main = Blueprint('main', __name__)

posts = [
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
def landing():
    return render_template('main/landing.html')


@main.route("/home")
def home():
    return render_template('main/home.html', posts=posts, title='Feed')