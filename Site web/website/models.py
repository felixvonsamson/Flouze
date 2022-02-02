from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    flouze = db.Column(db.Integer, default=0)
    stars = db.Column(db.Integer, default=0)
