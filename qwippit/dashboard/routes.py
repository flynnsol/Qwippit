from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify

dash = Blueprint('dash', __name__)


@dash.route("/", subdomain='dash')
def dash_home():
    return render_template('dash/home.html', title='Dashboard Home')