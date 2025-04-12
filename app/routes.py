from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from app import app
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, ExerciseForm, WorkoutForm
from app.models import User, Exercise, Workout, WorkoutExercise, ExerciseSet
from app import db
import sqlalchemy as sql
from flask_login import login_user, current_user, logout_user, login_required


#TODO: Write getter and setter functions



@app.route('/')
@app.route('/home')
def home():
    workouts = Workout.query.all()
    return render_template('home.html', title='Home', workouts=workouts)

@app.route('/workout', methods=['GET', 'POST'])
def workout():
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(sql.desc(Workout.date)).all()
    return render_template('workout.html', title='Home', workouts=workouts)


@app.route('/workout/new', methods=['GET', 'POST'])
def new_workout():
    form = WorkoutForm()
    user_exercises = Exercise.query.filter_by(user_id=current_user.id).all()
    exercise_choices = []

    for ex in user_exercises:
        exercise_choices.append((ex.id, ex.exercise_name))

    for exercise_form in form.exercises:
        exercise_form.exercise_id.choices = exercise_choices

    if form.validate_on_submit():
        print("Form validated successfully!")  # Debugging
        workout = add_workout(form)
        db.session.flush()

        for exercise_entry in form.exercises.data:
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise_entry['exercise_id'],
            )
            db.session.add(workout_exercise)
            db.session.flush()

            for set_entry in exercise_entry['sets']:
                exercise_set = ExerciseSet(
                    workout_exercise_id=workout_exercise.id,
                    set_number=set_entry['sets'],
                    reps=set_entry['reps'],
                    weight=set_entry['weight']
                )
                db.session.add(exercise_set)

        db.session.commit()
        flash('Workout created successfully!', 'success')
        return redirect(url_for('workout'))
    return render_template('new_workout.html', title='New Workout', form=form, legend='New Workout')


@app.route('/get_exercises', methods=['GET'])
@login_required
def get_exercises():
    user_exercises = Exercise.query.filter_by(user_id=current_user.id).all()
    exercises = []
    
    for exercise in user_exercises:
        exercises.append({
            'id': exercise.id,
            'name': exercise.exercise_name
        })
    
    return jsonify({'exercises': exercises})


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


@app.route("/workout/<int:workout_id>")
def single_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    return render_template('single_workout.html', title=workout.title, workout=workout)


@app.route("/workout/<int:workout_id>/update", methods=['GET', 'POST'])
@login_required
def update_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != current_user.id:
        abort(403)
    
    form = WorkoutForm()
    
    user_exercises = Exercise.query.filter_by(user_id=current_user.id).all()
    exercise_choices = [(ex.id, ex.exercise_name) for ex in user_exercises]
    
    for exercise_form in form.exercises:
        exercise_form.exercise_id.choices = exercise_choices
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
           
            workout.title = form.title.data
            workout.date = form.date.data
            workout.notes = form.notes.data
            

            for workout_exercise in workout.workout_exercises[:]: 
                db.session.delete(workout_exercise)
            
            for exercise_entry in (form.exercises.data):
                if exercise_entry['exercise_id']:
                    workout_exercise = WorkoutExercise(
                        workout_id=workout.id,
                        exercise_id=exercise_entry['exercise_id']
                    )
                    db.session.add(workout_exercise)
                    db.session.flush() 
                    

                    for set_entry in (exercise_entry['sets']): 
                        if set_entry.get('sets') and set_entry.get('reps') and set_entry.get('weight'):
                            exercise_set = ExerciseSet(
                                workout_exercise_id=workout_exercise.id,
                                set_number=set_entry['sets'],
                                reps=set_entry['reps'],
                                weight=set_entry['weight']
                            )
                            db.session.add(exercise_set)
            
            db.session.commit()
            flash('Workout updated successfully!', 'success')
            return redirect(url_for('workout', workout_id=workout.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating workout: {str(e)}', 'danger')
            return render_template('new_workout.html', title='Update Workout', form=form, legend='Update Workout')
    
    elif request.method == 'GET':
        form.title.data = workout.title
        form.date.data = workout.date
        form.notes.data = workout.notes
        
        while len(form.exercises) > 0:
            form.exercises.pop_entry()
        
        for exercise in workout.workout_exercises:
            exercise_data = {
                'exercise_id': exercise.exercise_id,
                'sets': []
            }
            
            for set_item in exercise.exercise_sets:
                set_data = {
                    'sets': set_item.set_number,
                    'reps': set_item.reps,
                    'weight': set_item.weight
                }
                exercise_data['sets'].append(set_data)
            
            form.exercises.append_entry(exercise_data)
            
            form.exercises[-1].exercise_id.choices = exercise_choices
    
    if form.errors:
        print(f"Form validation errors: {form.errors}")
        flash('There were errors in your form. Please check and try again.', 'danger')
    return render_template('new_workout.html', title='Update Workout', form=form, legend='Update Workout')


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


def add_workout(form):
    workout = Workout(date=form.date.data, 
                      title=form.title.data, 
                      user_id=current_user.id, 
                      notes=form.notes.data
                      )
    db.session.add(workout)
    return workout


