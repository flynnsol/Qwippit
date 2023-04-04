from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
import re


class QwippForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(max=256)])

    submit = SubmitField('Qwipp It')

    def extract_hashtags(self):
        hashtags = re.findall(r"#(\w+)", self.content.data)
        return hashtags


class QwillForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=64)])
    content = TextAreaField('Content', validators=[DataRequired()])

    submit = SubmitField('Create Qwill')

    def extract_hashtags(self):
        hashtags = re.findall(r"#(\w+)", self.content.data)
        return hashtags