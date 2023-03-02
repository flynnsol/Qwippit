from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class QwippForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(max=256)])

    submit = SubmitField('Qwipp It')