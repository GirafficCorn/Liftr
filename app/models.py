from typing import Optional
import sqlalchemy as sql
import sqlalchemy.orm as orm
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username : orm.Mapped[str] = orm.mapped_column(sql.String(64), unique=True)
    email: orm.Mapped[str] = orm.mapped_column(sql.String(120), unique=True)
    password_hash: orm.Mapped[str] = orm.mapped_column(sql.String(256))
    exercises: orm.Mapped[list['Exercise']] = orm.relationship(back_populates='author')
    workouts: orm.Mapped[list['Workout']] = orm.relationship(back_populates='user')


    def __repr__(self):
        return f'Username: {self.username}, Email: {self.email}'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Exercise(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    exercise_name: orm.Mapped[str] = orm.mapped_column(sql.String(120))
    description: orm.Mapped[Optional[str]] = orm.mapped_column(sql.String(256), )
    user_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(User.id)) 
    author : orm.Mapped[User] = orm.relationship(back_populates='exercises')

    workout_exercises: orm.Mapped[list['WorkoutExercise']] = orm.relationship('WorkoutExercise', back_populates='exercise')

    def __repr__(self):
        return f'Exercise Name: {self.exercise_name}, Description: {self.description}, Author: {self.author}'
    

#TODO Add weight
class Workout(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    date: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime, default=lambda: datetime.now(timezone.utc))
    title: orm.Mapped[str] = orm.mapped_column(sql.String(120))
    user_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(User.id))
    notes: orm.Mapped[str] = orm.mapped_column(sql.String(300))
    
    user: orm.Mapped['User'] = orm.relationship(back_populates='workouts')
    workout_exercises: orm.Mapped[list['WorkoutExercise']] = orm.relationship('WorkoutExercise', back_populates='workout')


class ExerciseSet(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    workout_exercise_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey('workout_exercise.id'), nullable=False)
    set_number: orm.Mapped[int] = orm.mapped_column(sql.Integer, nullable=False)
    weight: orm.Mapped[float] = orm.mapped_column(sql.Float, nullable=True) 
    reps: orm.Mapped[int] = orm.mapped_column(sql.Integer, nullable=False)

    workout_exercise: orm.Mapped['WorkoutExercise'] = orm.relationship(
        'WorkoutExercise',
        back_populates='exercise_sets'
    )

class WorkoutExercise(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)  # New primary key
    workout_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey('workout.id'), nullable=False)
    exercise_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey('exercise.id'), nullable=False)

    workout: orm.Mapped['Workout'] = orm.relationship('Workout', back_populates='workout_exercises')
    exercise: orm.Mapped['Exercise'] = orm.relationship('Exercise', back_populates='workout_exercises')
    exercise_sets: orm.Mapped[list['ExerciseSet']] = orm.relationship(
        'ExerciseSet',
        back_populates='workout_exercise',
        cascade="all, delete-orphan"
    )




@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

