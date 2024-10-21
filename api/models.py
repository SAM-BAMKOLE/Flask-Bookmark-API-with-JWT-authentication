from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# create user model
class User (db.Model, UserMixin):
    # __tablename__ = "user"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    tasks = db.relationship("Task")

    def to_json(self):
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "password": self.password,
            "tasks": self.tasks,
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(1000))
    datetime = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.String(15), default="UNCOMPLETED")
    activities = db.Column(db.String(2000))
    creator = db.Column(db.Integer, db.ForeignKey("user.id"))

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "datetime": self.datetime,
            "status": self.status,
            "activities": self.activities,
            "creator": self.creator,
        }