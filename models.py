from flask_login import UserMixin
from dotenv import load_dotenv

from datetime import datetime, timedelta
import os

from database import db

load_dotenv()

TIME_DELTA = int(os.environ.get("TIME_DELTA"))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    link = db.relationship("Link", uselist=False, backref="user")
    results = db.relationship("GameResult", backref="user")


class Link(db.Model):
    __tablename__ = "links"
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(10), nullable=False, unique=True)
    created = db.Column(db.DateTime, default=datetime.now())
    exp_date = db.Column(
        db.DateTime, default=datetime.now() + timedelta(days=TIME_DELTA)
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    active = db.Column(db.Boolean, default=True)


class GameResult(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    win = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
