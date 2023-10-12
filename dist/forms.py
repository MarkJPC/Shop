from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from dist.models import User


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class PhotoForm(FlaskForm):
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png','jpeg'])])


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])

    cover_photo = FileField('Cover Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    album_photos = FieldList(FormField(PhotoForm), min_entries=1, max_entries=20)

    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class AboutForm(FlaskForm):
    content = TextAreaField('Please enter your information', validators=[DataRequired()])
    submit = SubmitField('Update')
