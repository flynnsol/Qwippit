import os
import secrets

import PIL.Image
from flask import url_for, current_app
from flask_login import current_user
from flask_mail import Message

from qwippit import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (250, 250)
    i = PIL.Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    if current_user.image_file.strip() != 'default.png'.strip():
        prev_picture = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
        if os.path.exists(prev_picture):
            os.remove(prev_picture)

    return picture_fn


def save_banner(form_banner):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_banner.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/banner_pics', picture_fn)

    output_size = (1500, 500)
    i = PIL.Image.open(form_banner)
    i.thumbnail(output_size)

    i.save(picture_path)
    if current_user.banner_file.strip() != 'default.png'.strip():
        prev_picture = os.path.join(current_app.root_path, 'static/banner_pics', current_user.banner_file)
        if os.path.exists(prev_picture):
            os.remove(prev_picture)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='support@qwippit.com',
                  recipients=[user.email])
    msg.body = f'''
To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then ignore this email and no changes will be made.
    '''
    mail.send(msg)


def send_verify_email(user):
    token = user.get_email_token()
    msg = Message('Verify Your Email',
                  sender='support@qwippit.com',
                  recipients=[user.email])
    msg.body = f'''
To verify your email, visit the following link:
{url_for('users.verify_email', token=token, _external=True)}

If you did not make this request then ignore this email and the account will not be verified.
    '''
    mail.send(msg)
