from flask.ext.wtf import Form
from wtforms import PasswordField
from wtforms import StringField
from wtforms.validators import DataRequired


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])