import os
from flask import render_template, url_for, flash, redirect, request, abort
from dist import app, db, bcrypt
from flask_login import current_user, login_required, logout_user, login_user
from dist.forms import LoginForm, PostForm
from dist.models import User, Post


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]



@app.route('/')
@app.route('/shop')
def shop():
    #user = User(username="admin", email="admin@shop.com", password="#shop@farm2000")
    return render_template('shop.html', title='Shop', posts=posts)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email="admin@shop.com").first()
        if form.email.data == "admin@shop.com" and form.password.data == "#shop@farm2000":
            login_user(user, remember=form.remember.data)
            return redirect(url_for('shop'))
        else:
            flash('Login Unsuccessful. Please check the username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
            


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('shop'))

"""
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    
    # create post form to pass into html page
    
    # check if form validates
        # create post object
        # add post to database and commit


@app.route('/post/<int:post_id/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):


@app.route('post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):


@app.route('/post/<int:post_id>')
def post(post_id)
"""



