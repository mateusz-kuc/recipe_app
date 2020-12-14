from datetime import datetime
from recipe_app import db, login_manager
from flask_login import UserMixin


#Potrzebne do remember me
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    history = db.relationship('History', backref='searcher', lazy=True)
    likes = db.relationship('Liked', backref='liker', lazy=True)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}'"
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_searched = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"History('{self.title}', '{self.date_searched}','{self.recipe_id}')"
class Liked(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_searched = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Liked('{self.title}', '{self.date_searched}','{self.recipe_id}')"
