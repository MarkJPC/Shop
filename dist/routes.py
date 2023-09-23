import os, secrets
from flask import render_template, url_for, flash, redirect, request, abort
from dist import app, db, bcrypt
from flask_login import current_user, login_required, logout_user, login_user
from dist.forms import LoginForm, PostForm
from dist.models import User, Post
from PIL import Image

user = User(username="admin", email="admin@shop.com", password="#shop@farm2000")

"""
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
"""


@app.route('/')
@app.route('/shop')
def shop():
    page = request.args.get('page', 1, type=int)
    # get only a specific amount of posts per page
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
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
    #db.session.add(user)
    #db.session.commit()
    return redirect(url_for('shop'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    
    # create post form to pass into html page
    form = PostForm()
    
    # check if form validates
    if form.validate_on_submit():

        # deal with picture
        if form.picture.data:
            print("picture exists")
            picture_file = save_picture(form.picture.data)

            # create post object
            post = Post(title=form.title.data, 
                        price=form.price.data, 
                        image_file=picture_file,
                        content=form.content.data,
                        author=current_user)
            # add post to database and commit
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('shop'))
        else:
            print("picture does not exist")
    return render_template('create_post.html',
                           title='New Post',
                           form=form,
                           legend='New Post')


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)

            post.title = form.title.data
            post.price = form.price.data
            post.image_file = picture_file
            post.content = form.content.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.price.data = post.price
        form.picture.data = post.image_file
        form.content.data = post.content
    return render_template('create_post.html', 
                           title='Update Post',
                           form=form, 
                           legend='Update Post')

@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('shop'))

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)



