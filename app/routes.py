from flask import render_template, url_for, flash, redirect, request
from app import app
import datetime
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, ExerciseForm
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
        register_user(form)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form)
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

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        update_profile(form)
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', form=form)

#Fix get_user function to utilize get_exercise
@app.route('/exercise', methods=['GET', 'POST'])
@login_required
def exercise():
    form = ExerciseForm()
    if form.validate_on_submit():
        add_exercise = Exercise(exercise_name=form.exercise_name.data, author=current_user)
        db.session.add(add_exercise)
        db.session.commit()
        flash(f'Exercise added successfully!', 'success')
        return redirect(url_for('exercise'))
    exercises = db.session.scalars(sql.select(Exercise).where(Exercise.user_id == current_user.id))
    return render_template('exercise.html', exercise=exercises, form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
    
def register_user(form):
    user = User(username=form.username.data, email=form.email.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash(f'Account created successfully!', 'success')

def get_user(form):
    user = db.session.scalar(sql.select(User).where(User.email == form.email.data))
    return user

def update_profile(form):
    current_user.username = form.username.data
    current_user.email = form.email.data
    db.session.commit()
    flash('Your account has been updated!', 'success')

'''def add_exercise(form):
    exercise = Exercise(exercise_name=form.exercise_name.data, description=form.description.data)
    db.session.add(exercise)
    db.session.commit()
    flash(f'Exercise added successfully!', 'success')'''



