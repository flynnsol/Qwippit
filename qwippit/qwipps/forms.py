from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class QwippForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(max=256)])

    submit = SubmitField('Qwipp It')


class QwillForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=32)])
    content = TextAreaField('Content', validators=[DataRequired()])

    submit = SubmitField('Create Qwill')