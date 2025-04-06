from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Exercise
from app import db
import sqlalchemy as sql
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=32)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sql.select(User).where(User.username == username.data))
        if user:
            raise ValidationError('Username already exists.')
        
    def validate_email(self, email):
        user = db.session.scalar(sql.select(User).where(User.email == email.data))
        if user:
            raise ValidationError('Email already exists.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ExerciseForm(FlaskForm):
    exercise_name = StringField('Exercise Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save Exercise')

    #TODO fix case sensitive portion
    def validate_exercise_name(self, exercise_name):
        exercise = db.session.scalar(sql.select(Exercise).where(Exercise.exercise_name == exercise_name.data))
        if exercise:
            raise ValidationError('Exercise already exists.')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=32)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = db.session.scalar(sql.select(User).where(User.username == username.data))
            if user:
                raise ValidationError('Username already exists.')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = db.session.scalar(sql.select(User).where(User.email == email.data))
            if user:
                raise ValidationError('Email already exists.')