from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(400)
def error_400(error):
    return render_template('errors/400.html')


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html')


@errors.app_errorhandler(405)
def error_405(error):
    return render_template('errors/405.html')


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html')


@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html')