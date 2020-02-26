import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# This is 'object relational mapping' which is supposed to map a class to my SQL table  
class RegisteredUsers(db.Model):
    __tablename__="Registered_Users"
    User_Id = db.Column(db.Integer, primary_key=True)
    User_Name = db.Column(db.String)
    Password = db.Column(db.String)

