import os, secrets
from flask import render_template, url_for, flash, redirect, request, abort, Markup
from dist import app, db, bcrypt
from flask_login import current_user, login_required, logout_user, login_user
from dist.forms import LoginForm, PostForm, AboutForm
from dist.models import User, Post, CoverPhoto, AlbumPhoto, AboutContent
from PIL import Image

user = User(username="admin", email="admin@shop.com", password="#shop@farm2000")
about = AboutContent(content="")

@app.route('/')
@app.route('/shop')
def shop():
    page = request.args.get('page', 1, type=int)
    # get only a specific amount of posts per page
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    return render_template('shop.html', title='Shop', posts=posts)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if current_user.is_authenticated:
        logged_in = True
    else:
        logged_in = False

    if logged_in:
        # create the form
        form = AboutForm()
        about_content = AboutContent.query.first()

        if form.validate_on_submit():
            print("form validated")
            content = form.content.data
            about_content.content = content
            db.session.commit()

            return redirect(url_for('contact'))
        else:
            print("form did not validate")
        form.content.data = about_content.content

    return render_template('contact.html', title='Contact', form=form, about=about_content, logged_in=logged_in)


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
    #db.session.add(about)
    #db.session.add(user)
    #db.session.commit()
    return redirect(url_for('shop'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (1000, 1000)
    i = Image.open(form_picture)
    i.resize(output_size, Image.LANCZOS)
    i.save(picture_path)

    return picture_fn


def delete_picture(picture_fn):
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    if os.path.isfile(picture_path):
        os.remove(picture_path)


@app.route('/delete_photo', methods=['POST'])
def delete_photo():
    picture_fn = request.form.get('picture_fn')
    delete_picture(picture_fn)

    cover_photo = CoverPhoto.query.filter_by(filename=picture_fn).first()
    if cover_photo:
        db.session.delete(cover_photo)
        db.session.commit()
    
    album_photo = AlbumPhoto.query.filter_by(filename=picture_fn).first()
    if album_photo:
        db.session.delete(album_photo)
        db.session.commit()
        

    return '', 204  # Return an empty response with a 204 status code


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():

    post_exists = Post.query.first()
    
    # create post form to pass into html page
    form = PostForm()
    
    # check if form validates
    if form.validate_on_submit():
        print("form validated")
        # make sure cover photo exists
        if form.cover_photo.data:
            print("picture exists")
            # save cover photo
            cover_photo_filename = save_picture(form.cover_photo.data)
            cover_photo = CoverPhoto(filename=cover_photo_filename)

            # save album photos
            album_photos = []
            print(request.files.getlist('album_photos-0-photo'))
            for photo_file in request.files.getlist('album_photos-0-photo'):
                if photo_file:
                    print(photo_file)
                    album_photo_filename = save_picture(photo_file)
                    album_photo = AlbumPhoto(filename=album_photo_filename)
                    album_photos.append(album_photo)

            # create post object
            post = Post(title=form.title.data, 
                        price=form.price.data, 
                        content=form.content.data,
                        author=current_user,
                        cover_photo=cover_photo,
                        album_photos=album_photos)

            # add post to database and commit
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('shop'))
        else:
            print("picture does not exist")

    else:
        print(form.errors)
    
    return render_template('create_post.html',
                           title='New Post',
                           form=form,
                           legend='New Post')



@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post_exists = Post.query.first()
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        if form.cover_photo.data:
            cover_photo_filename = save_picture(form.cover_photo.data)
            if post.cover_photo:
                post.cover_photo.filename = cover_photo_filename
            else:
                cover_photo = CoverPhoto(filename=cover_photo_filename)
                post.cover_photo = cover_photo

        if form.album_photos.data[0]['photo']:
            print(request.files.getlist('album_photos-0-photo'))
            for photo_file in request.files.getlist('album_photos-0-photo'):
                print(photo_file)
                album_photo_filename = save_picture(photo_file)
                
                new_album_photo = AlbumPhoto(filename=album_photo_filename, post_id=post.id)
                db.session.add(new_album_photo)


        post.title = form.title.data
        post.price = form.price.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.price.data = post.price
        form.content.data = post.content

    return render_template('create_post.html', 
                           title='Update Post',
                           form=form, 
                           legend='Update Post',
                           post=post)

@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    # delete associated album photos
    for photo in post.album_photos:
        delete_picture(photo.filename)
        db.session.delete(photo)
    delete_picture(post.cover_photo.filename)
    db.session.delete(post.cover_photo)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('shop'))

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)
