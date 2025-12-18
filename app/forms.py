from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 128)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('sender','Sender'),('receiver','Receiver')], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EncodeForm(FlaskForm):
    secret = StringField('Secret Message', validators=[DataRequired()])
    submit = SubmitField('Encode')

class DecodeForm(FlaskForm):
    snippets = TextAreaField('Paste Received Snippets (one per line)', validators=[DataRequired()])
    submit = SubmitField('Decode')
