from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(), default = datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     name=forgery_py.name.full_name(),
                     created_at=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<User %r>' % self.username

class Pies(db.Model):
    __tablename__ = 'pies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(), default = datetime.utcnow)

    @staticmethod
    def add_menu():
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        import emoji

        names = [emoji.emojize('Apple Pie :green_apple:', use_aliases=True),
        emoji.emojize('Pumpkin Pie :jack_o_lantern:', use_aliases=True),
        emoji.emojize('Banana Cream Pie :banana:', use_aliases=True),
        emoji.emojize('Cherry Pie :cherries:', use_aliases=True)]
        descriptions = ['Apples, Cinnamon, Sugar', 'Like a PSL without the latte', 'Bananas, pudding, cream. Very healthy', 'Wild as Friday Night']

        seed()
        for i in range(0, len(names)):
            u = Pies(name=names[i],
                     description=descriptions[i],
                     created_at=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    pie_id = db.Column(db.Integer, db.ForeignKey('pies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(), default = datetime.utcnow)

    users = db.relationship(User)
    pies = db.relationship(Pies)

    @staticmethod
    def generate_orders(count=500):
        from random import seed, randint

        seed()
        user_count = User.query.count()
        pie_count = Pies.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            p = Pies.query.offset(randint(0,pie_count-1)).first()
            o = Orders(pie_id=p.id,user_id=u.id,
                       created_at=u.created_at + timedelta(days = randint(0,365)))
            db.session.add(o)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
