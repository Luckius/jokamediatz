import os
import secrets
from PIL import Image
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, abort,g
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,GamescmtForm ,EducationcmtForm,MessagesForm,
                              BussnescmtForm ,PostForm,MessageForm,AddCommentForm, RequestResetForm, ResetPasswordForm)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed,FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flaskblog.models import (User, Post ,Messages ,Games ,Education ,Jokanews ,Bussnes ,Pvtmessage , Notification,
                               Gamescmt ,Educationcmt ,Bussnescmt)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import flask_whooshalchemy as wa












@app.route("/")
@app.route("/home")
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=50)
    return render_template('home.html', posts=posts)


@app.route("/message")
@login_required
def message():
    page = request.args.get('page', 1, type=int)
    messages = Messages.query.order_by(Messages.date_posted.desc()).paginate(page=page, per_page=25)
    return render_template('message.html', messages=messages)


@app.route("/album")
@login_required
def album():
    page = request.args.get('page', 1, type=int)
    ouralbum = Messages.query.order_by(Messages.date_posted.desc()).paginate(page=page, per_page=25)
    return render_template('album.html', ouralbum=ouralbum)



@app.route("/active")
@login_required
def active():
    peples = User.query.all()
    return render_template('peples.html', peples=peples)



@app.route("/games")
@login_required
def games():
    mygames = Games.query.limit(1).all()
    page = request.args.get('page', 1, type=int)
    comments = Gamescmt.query.order_by(Gamescmt.date_posted.desc()).paginate(page=page, per_page=50)
    return render_template('showgames.html', mygames=mygames, comments=comments)


@app.route("/education")
@login_required
def education():
    myeducation = Education.query.limit(1).all()
    page = request.args.get('page', 1, type=int)
    comments = Educationcmt.query.order_by(Educationcmt.date_posted.desc()).paginate(page=page, per_page=50)
    return render_template('showeducation.html', myeducation=myeducation, comments=comments)


@app.route("/bussnes")
@login_required
def bussnes():
    mybussnes = Bussnes.query.limit(1).all()
    page = request.args.get('page', 1, type=int)
    comments = Bussnescmt.query.order_by(Bussnescmt.date_posted.desc()).paginate(page=page, per_page=50)
    return render_template('showbussnes.html', mybussnes=mybussnes, comments=comments)



@app.route("/jokanews")
@login_required
def jokanews():
    page = request.args.get('page', 1, type=int)
    myjokanews = Jokanews.query.order_by(Jokanews.date_posted.desc()).paginate(page=page, per_page=25)
    return render_template('showjokanews.html', myjokanews=myjokanews)


@app.route("/")
@app.route("/jokamedia")
def jokamedia():
    return render_template('jokamedia.html')



@app.route("/jokaforum")
@login_required
def jokaforum():
    return render_template('jokaforum.html')




@app.route("/about")
@login_required
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            user.last_seen = datetime.utcnow()
            db.session.commit()
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('jokamedia'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')



def my_picture(form_photo):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_photo.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_photo)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn




# Uploads settings the config that not taken into a init.py file
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + 'static/profile_pics'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB
photos = UploadSet('photos', IMAGES)


#form for photo posting
class UploadForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content', validators=[DataRequired()])
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')


@login_required
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        new_file = file_url
        message = Messages(title=form.title.data, content=form.content.data,author=current_user, image_file=new_file)
        db.session.add(message)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('message'))
    else:
        file_url = None
    return render_template('create_message.html', form=form)



#form for photo posting
class GamesForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content', validators=[DataRequired()])
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')


@login_required
@app.route('/games_file', methods=['GET', 'POST'])
def games_file():
    form = GamesForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        new_file = file_url
        games = Games(title=form.title.data, content=form.content.data,author=current_user, image_file=new_file)
        db.session.add(games)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('games'))
    else:
        file_url = None
    return render_template('games.html', form=form)




#form for photo posting
class EducationForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content', validators=[DataRequired()])
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')


@login_required
@app.route('/education_file', methods=['GET', 'POST'])
def education_file():
    form = EducationForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        new_file = file_url
        education = Education(title=form.title.data, content=form.content.data,author=current_user, image_file=new_file)
        db.session.add(education)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('education'))
    else:
        file_url = None
    return render_template('education.html', form=form)




#form for photo posting
class BussnesForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content', validators=[DataRequired()])
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')




@login_required
@app.route('/bussnes_file', methods=['GET', 'POST'])
def bussnes_file():
    form = BussnesForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        new_file = file_url
        bussnes = Bussnes(title=form.title.data, content=form.content.data,author=current_user, image_file=new_file)
        db.session.add(bussnes)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('bussnes'))
    else:
        file_url = None
    return render_template('bussnes.html', form=form)




#form for photo posting
class JokanewsForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content', validators=[DataRequired()])
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')



@login_required
@app.route('/jokanews_file', methods=['GET', 'POST'])
def jokanews_file():
    form = JokanewsForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        new_file = file_url
        jokanews = Jokanews(title=form.title.data, content=form.content.data,author=current_user, image_file=new_file)
        db.session.add(jokanews)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('jokanews'))
    else:
        file_url = None
    return render_template('jokanews.html', form=form)



#comment



@app.route("/gamescmt", methods=['GET', 'POST'])
@login_required
def gamescmt():
    form = GamescmtForm()
    if form.validate_on_submit():
        comment = Gamescmt(content=form.content.data, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been aded!', 'success')
        return redirect(url_for('games'))
    return render_template('gamescmt.html', title='New Post',
                           form=form, legend='New Post')




@app.route("/educationcmt", methods=['GET', 'POST'])
@login_required
def educationcmt():
    form = EducationcmtForm()
    if form.validate_on_submit():
        comment = Educationcmt(content=form.content.data, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been aded!', 'success')
        return redirect(url_for('education'))
    return render_template('educationcmt.html', title='New Post',
                           form=form, legend='New Post')





@app.route("/bussnescmt", methods=['GET', 'POST'])
@login_required
def bussnescmt():
    form = BussnescmtForm()
    if form.validate_on_submit():
        comment = Bussnescmt(content=form.content.data, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been aded!', 'success')
        return redirect(url_for('bussnes'))
    return render_template('bussnescmt.html', title='New Post',
                           form=form, legend='New Post')






@app.route("/myuser/<string:username>")
@login_required
def user_message(username):
    page = request.args.get('page', 1, type=int)
    myuser = User.query.filter_by(username=username).first_or_404()
    messages = Messages.query.filter_by(author=myuser)\
        .order_by(Messages.date_posted.desc())\
        .paginate(page=page, per_page=25)
    return render_template('message.html', messages=messages, myuser=myuser)





@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)






@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')






@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))





@app.route("/delete_message/<int:message_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_message(message_id):
    message = Messages.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('message'))





@app.route("/delete_games/<int:message_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_games(message_id):
    message = Games.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('games'))





@app.route("/delete_education/<int:message_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_education(message_id):
    message = Education.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('education'))




@app.route("/delete_bussnes/<int:message_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_bussnes(message_id):
    message = Bussnes.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('bussnes'))



@app.route("/delete_jokanews/<int:message_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_jokanews(message_id):
    message = Jokanews.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('jokanews'))



@app.route("/delete_gamescmt/<int:message_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_gamescmt(message_id):
    message = Gamescmt.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('games'))



@app.route("/delete_educationcmt/<int:message_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_educationcmt(message_id):
    message = Educationcmt.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('education'))




@app.route("/delete_bussnescmt/<int:message_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_bussnescmt(message_id):
    message = Bussnescmt.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('bussnes'))






@app.route("/user/<string:username>")
@login_required
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=50)
    return render_template('user_posts.html', posts=posts, user=user)




@app.route("/meuser/<string:username>")
@login_required
def meuser_messages(username):
    page = request.args.get('page', 1, type=int)
    meuser = User.query.filter_by(username=username).first_or_404()
    messages = Messages.query.filter_by(author=meuser)\
        .order_by(Messages.date_posted.desc())\
        .paginate(page=page, per_page=25)
    return render_template('meuser_messages.html', messages=messages, meuser=meuser)






def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Wellcome to Luck Kajoka @ Jokamediatz
To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
this link will be expired in 30 minutes
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)




@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!','warning')
        return redirect(url_for('user_posts', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username),'success')
    return redirect(url_for('user_posts', username=username))




@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!','warning')
        return redirect(url_for('user_posts', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username),'success')
    return redirect(url_for('user_posts', username=username))


@app.route('/search')
def search():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    messages = Messages.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    games = Games.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    education = Education.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    jokanews = Jokanews.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    bussnes = Bussnes.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    gamescmt = Gamescmt.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    educationcmt = Educationcmt.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    bussnescmt = Bussnescmt.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    return render_template('search.html',posts=posts,messages=messages,games=games,
                           education=education,jokanews=jokanews,bussnes=bussnes,gamescmt=gamescmt,
                           educationcmt=educationcmt,bussnescmt=bussnescmt)

@app.route('/usersearch')
@login_required
def usersearch():
    page = request.args.get('page', 1, type=int)
    users = User.query.whoosh_search(request.args.get('query')).paginate(page=page, per_page=25)
    return render_template('usersearch.html',users=users)





@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessagesForm()
    if form.validate_on_submit():
        user.add_notification('unread_message_count', user.new_messages())
        msg = Pvtmessage(author=current_user, recipient=user,body=form.content.data)
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent to {}'.format(recipient),'success')
        return redirect(url_for('user_posts', username=recipient))
    return render_template('send_message.html', title=('Send Message'),
                           form=form, recipient=recipient)




@app.route('/pvtmessages')
@login_required
def pvtmessages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
    Pvtmessage.timestamp.desc()).paginate(page=page, per_page=25)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('pvtmessages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)



@app.route("/delete_pvtmessage/<int:message_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_pvtmessage(message_id):
    message = Pvtmessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('message has been deleted!', 'success')
    return redirect(url_for('pvtmessages'))




@app.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])





@app.errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404


@app.errorhandler(403)
def error_403(error):
    return render_template('403.html'), 403


@app.errorhandler(500)
def error_500(error):
    return render_template('500.html'), 500
