from typing import Optional
import sqlalchemy as sql
import sqlalchemy.orm as orm
from app import db

class User(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username : orm.Mapped[str] = orm.mapped_column(sql.String(32), unique=True)
    email: orm.Mapped[str] = orm.mapped_column(sql.String(120), unique=True)
    password_hash: orm.Mapped[str] = orm.mapped_column(sql.String(256))
    exercises: orm.WriteOnlyMapped['Exercise'] = orm.relationship(back_populates='author')

    def __repr__(self):
        return f'Username: {self.username}, Email: {self.email}'


class Exercise(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    exercise_name: orm.Mapped[str] = orm.mapped_column(sql.String(120))
    description: orm.Mapped[Optional[str]] = orm.mapped_column(sql.String(256), )
    user_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(User.id)) 
    author : orm.WriteOnlyMapped['User'] = orm.relationship(back_populates='exercises')

    def __repr__(self):
        return f'Exercise Name: {self.exercise_name}, Description: {self.description}, Author: {self.author}'