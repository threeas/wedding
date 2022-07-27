from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Length, Email,EqualTo

class ContactForm(FlaskForm):
    fullname = StringField("Enter your Fullname", validators=[DataRequired(message="Excuse me, enter your fullname"),Length(min=5)])
    email = StringField("Email",validators=[Email()])
    message = TextAreaField()
    submit = SubmitField("Submit Now")

class SignupForm(FlaskForm):
    firstname = StringField("", validators=[DataRequired(message="Please supply your First Name")])
    lastname = StringField("",validators=[DataRequired(message="Please supply your Last Name")])
    email = StringField("",validators=[Email("A valid email is required")])
    password = PasswordField("",validators=[DataRequired(),Length(min=4)])
    confirm_pass = PasswordField("",validators=[EqualTo("password")])
    submit = SubmitField("Sign Up Now")

    # csrf_token

# pip install email_validator