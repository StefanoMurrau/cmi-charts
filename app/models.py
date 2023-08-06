from datetime import datetime, timezone
from flask import current_app
from flask_login import UserMixin
from app.database import db


SCHEMA = current_app.config.get("PROJECT_NAME")


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": SCHEMA, "comment": "Personal data table for application users"}
    id = db.Column(db.Integer(), primary_key=True, comment="Primary key of the table")
    mail = db.Column(db.String(255), nullable=False, unique=True, comment="User's email used as a unique identifier during authentication")
    password = db.Column(db.String(255), nullable=False, comment="User password encrypted with BCrypt")
    user_actions = db.relationship("User_actions", cascade="all, delete-orphan", lazy="select", backref=db.backref("users",lazy="joined"))


class Actions(db.Model):
    __tablename__ = "actions"
    __table_args__ = {"schema": SCHEMA, "comment": "Support table with all possible user actions"}
    id = db.Column(db.Integer(), primary_key=True, comment="Primary key of the table")
    name = db.Column(db.String(255), nullable=False, comment="Identification name of the action")
    description = db.Column(db.Text, nullable=True, comment="Extended description of the action")
    user_actions = db.relationship("User_actions", cascade="all, delete-orphan", lazy="select", backref=db.backref("actions",lazy="joined"))


class User_actions(db.Model):
    __tablename__ = "user_actions"
    __table_args__ = {"schema": SCHEMA, "comment": "Table of actions performed by users"}
    id = db.Column(db.Integer, primary_key=True, comment="Primary key of the table")
    user_id = db.Column(db.Integer(), db.ForeignKey(Users.id), nullable=False, comment="Foreign key to the users table")
    action_id = db.Column(db.Integer(), db.ForeignKey(Actions.id), nullable=False, comment="Foreign key to the actions table")
    remote_addr = db.Column(db.String(255), nullable=True, default=None, comment="User's IP")
    http_user_agent = db.Column(db.String(255), nullable=True, default=None, comment="User's browser")
    datetime = db.Column(db.String(25), default=datetime.now(timezone.utc).astimezone().isoformat("T", "seconds"), nullable=False, comment="Datetime")
