from flask import render_template, url_for
from app import app
import datetime


workout = {
    'User': 'Brandon',
    'Date': datetime.date.today(),
    'Exercises': ['Bench', 'Tricep Pushdowns', 'Dips', 'Skull Crushers']

}





@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/workout')
def workouts():
    return render_template('workout.html', title='Workouts', workout=workout)
    