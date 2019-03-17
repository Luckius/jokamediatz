from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app
from flask_login import UserMixin
import flask_whooshalchemy as wa
import json
from time import time


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))





followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)



class User(db.Model, UserMixin):

    __searchable__ = ['username']
    id = db.Column(db.Integer, primary_key=True)
    last_seen = db.Column(db.DateTime)
    joined_day = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    messages = db.relationship('Messages', backref='author', lazy=True)
    games = db.relationship('Games', backref='author', lazy=True)
    education = db.relationship('Education', backref='author', lazy=True)
    jokanews = db.relationship('Jokanews', backref='author', lazy=True)
    bussnes = db.relationship('Bussnes', backref='author', lazy=True)
    gamescmt = db.relationship('Gamescmt', backref='author', lazy=True)
    bussnescmt = db.relationship('Bussnescmt', backref='author', lazy=True)
    educationcmt = db.relationship('Educationcmt', backref='author', lazy=True)
    notifications = db.relationship('Notification', backref='user',lazy='dynamic')
    messages_sent = db.relationship('Pvtmessage',foreign_keys='Pvtmessage.sender_id', backref='author', lazy='dynamic')
    messages_received = db.relationship('Pvtmessage', foreign_keys='Pvtmessage.recipient_id', backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)



    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Pvtmessage.query.filter_by(recipient=self).filter(
            Pvtmessage.timestamp > last_read_time).count()



    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n



    followed = db.relationship(
         'User', secondary=followers,
         primaryjoin=(followers.c.follower_id == id),
         secondaryjoin=(followers.c.followed_id == id),
         backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')




    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0


    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.date_posted.desc())



    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')




    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

wa.whoosh_index(app,User)






class Post(db.Model):
    __searchable__ = ['title','content']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

wa.whoosh_index(app,Post)




class Pvtmessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Pvtmessage {}>'.format(self.body)



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))





class Messages(db.Model):

    __searchable__ = ['title','content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"Messages('{self.title}', '{self.date_posted}', '{self.image_file}')"

wa.whoosh_index(app,Messages)



class Games(db.Model):

    __searchable__ = ['title','content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"Games('{self.title}', '{self.date_posted}', '{self.image_file}')"


wa.whoosh_index(app,Games)



class Education(db.Model):

    __searchable__ = ['title','content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"Education('{self.title}', '{self.date_posted}', '{self.image_file}')"


wa.whoosh_index(app,Education)


class Jokanews(db.Model):

    __searchable__ = ['title','content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"Jokanews('{self.title}', '{self.date_posted}', '{self.image_file}')"

wa.whoosh_index(app,Jokanews)




class Bussnes(db.Model):

    __searchable__ = ['title','content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"Bussnes('{self.title}', '{self.date_posted}', '{self.image_file}')"


wa.whoosh_index(app,Bussnes)




class Gamescmt(db.Model):

    __searchable__ = ['content']
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Gamescmt( '{self.date_posted}')"


wa.whoosh_index(app,Gamescmt)



class Educationcmt(db.Model):

    __searchable__ = ['content']
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Educationcmt( '{self.date_posted}')"


wa.whoosh_index(app,Educationcmt)




class Bussnescmt(db.Model):

    __searchable__ = ['content']
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Bussnescmt( '{self.date_posted}')"


wa.whoosh_index(app,Bussnescmt)
