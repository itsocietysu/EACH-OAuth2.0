import time
import datetime
import os

import jwt
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column
from sqlalchemy import UniqueConstraint
from sqlalchemy import (
    Integer, String, DateTime
)
from .base import db, Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    _password = Column('password', String(100))
    name = Column(String(80))
    access_type = Column(String(40), default='user', nullable=False)
    image_filename = Column(String(4000))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    def get_user_id(self):
        return self.id

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    @classmethod
    def query_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def update(cls, _id, data):
        from website.forms.user import save_image

        user = cls.query.filter_by(id=_id).first()
        if not user:
            return None
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            email_validation = User.query.filter_by(email=data['email']).all()
            if not len(email_validation):
                user.email = data['email']
        if 'image' in data:
            if user.image_filename and os.path.isfile(user.image_filename):
                os.remove(user.image_filename)
            user.image_filename = save_image(data['image'])
        with db.auto_commit():
            db.session.add(user)
        return user

    @classmethod
    def get_or_create(cls, profile):
        user = cls.query.filter_by(email=profile.email).first()
        if user:
            return user
        user = cls(email=profile.email, name=profile.name, image_filename=profile.image_filename)
        user._password = '!'
        with db.auto_commit():
            db.session.add(user)
        return user

    def to_dict(self, host):
        image = ''
        if self.image_filename:
            image = 'http://%s%s' % (host, self.image_filename[1:])
        return dict(id=self.id, name=self.name, email=self.email, access_type=self.access_type, image=image)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time.time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)


class Connect(Base):
    __tablename__ = 'connect'
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uc_connect'),
    )
    OAUTH1_TOKEN_TYPE = 'oauth1.0'

    id = Column(Integer, primary_key=True)
    sub = Column(String(255))
    user_id = Column(Integer, nullable=False)
    name = Column(String(20), nullable=False)
    token_type = Column(String(20))
    access_token = Column(String(255), nullable=False)
    # refresh_token or access_token_secret
    alt_token = Column(String(255))
    expires_at = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        if self.token_type == self.OAUTH1_TOKEN_TYPE:
            return dict(
                oauth_token=self.access_token,
                oauth_token_secret=self.alt_token,
            )
        return dict(
            access_token=self.access_token,
            refresh_token=self.alt_token,
            token_type=self.token_type,
            expires_at=self.expires_at,
        )

    @classmethod
    def create_token(cls, name, token, user):
        conn = cls.query.filter_by(user_id=user.id, name=name).first()
        if not conn:
            conn = cls(user_id=user.id, name=name)

        if 'oauth_token' in token:
            # save for OAuth 1
            conn.token_type = cls.OAUTH1_TOKEN_TYPE
            conn.access_token = token['oauth_token']
            conn.alt_token = token['oauth_token_secret']
        else:
            conn.access_token = token['access_token']
            conn.token_type = token.get('token_type', '')
            conn.alt_token = token.get('refresh_token', '')
            expires_in = token.get('expires_in', 0)
            if expires_in:
                conn.expires_at = int(time.time()) + expires_in

        conn.sub = token['sub']
        with db.auto_commit():
            db.session.add(conn)
        return conn
