from dist import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# create classes which make up the tables of the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    # this is how our object is printed
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# post class to hold our posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cover_photo = db.relationship('CoverPhoto', backref='post', lazy=True, uselist=False)
    album_photos = db.relationship('AlbumPhoto', backref='post', lazy=True)


    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"
    

# Classes for cover photo and album photos. Each post can have one cover photo and multiple album photos
class CoverPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(20), nullable=False, default='default.jpg')
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


class AlbumPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(20), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)