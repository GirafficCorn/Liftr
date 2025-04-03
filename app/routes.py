from flask import render_template, url_for, flash, redirect
from app import app
import datetime
from app.forms import RegistrationForm, LoginForm


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
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'test@test.com' and form.password.data == 'test':
            flash(f'Login Successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful', 'danger')
    return render_template('login.html', title='Login', form=form)
    