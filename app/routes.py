from flask import render_template, url_for, flash, redirect, request
from app import app
import datetime
from app.forms import RegistrationForm, LoginForm
from app.models import User, Exercise
from app import db
import sqlalchemy as sql
from flask_login import login_user, current_user, logout_user, login_required


workout = {
    'User': 'Brandon',
    'Date': datetime.date.today(),
    'Exercises': ['Bench', 'Tricep Pushdowns', 'Dips', 'Skull Crushers']

}





@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')


@app.route('/workout')
def workouts():
    return render_template('workout.html', title='Workouts', workout=workout)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sql.select(User).where(User.email == form.email.data))
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect('next')
            else:
                return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful, please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = db.session.scalar(sql.select(User).where(User.username == username))
    exercises = db.session.scalars(sql.select(Exercise).where(Exercise.user_id == user.id))
    return render_template('profile.html', user=user, exercises=exercises)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
    