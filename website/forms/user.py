import base64
import re
import json
import os

from wtforms.fields import StringField, PasswordField, HiddenField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
from wtforms.validators import StopValidation

from ..email import send_password_reset_email
from .base import BaseForm
from ..models import db, User
from ..auth import login
from ..media_resolver.mediaresolverfactory import MediaResolverFactory

from flask_babel import lazy_gettext as _l


class AuthenticateForm(BaseForm):
    email = EmailField(_l('Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(AuthenticateForm, self).__init__(*args, **kwargs)
        self._user = None

    def validate_password(self, field):
        email = self.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(field.data):
            raise StopValidation(_l('Email or password is invalid.'))
        self._user = user

    def login(self):
        if self._user:
            login(self._user, True)


def save_image(data):
    with open('website/def.image.json', 'r') as f:
        default_image = re.sub('data:image/(jpeg|png|jpg);base64,', '', json.load(f)['image'])
        f.close()
    if not data:
        resolver = MediaResolverFactory.produce('image', base64.b64decode(default_image))
        return resolver.resolve()
    value = re.sub('data:image/(jpeg|png|jpg);base64,', '', data)
    resolver = MediaResolverFactory.produce('image', base64.b64decode(value))
    return resolver.resolve()


class UserCreationForm(BaseForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    email = EmailField(_l('Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    avatar = FileField(_l('Avatar'),
                       render_kw={'accept': 'image/png, image/jpeg, image/jpg', 'onchange': 'loadImage(this)'})
    hidden_img = HiddenField(validators=[DataRequired()])

    def validate_email(self, field):
        email = field.data.lower()
        user = User.query.filter_by(email=email).first()
        if user:
            raise StopValidation(_l('Email has been registered.'))

    def signup(self):
        name = self.name.data
        email = self.email.data.lower()
        image = save_image(self.hidden_img)
        user = User(name=name, email=email, image_filename=image)
        user.password = self.password.data
        with db.auto_commit():
            db.session.add(user)
        login(user, True)
        return user


class UserEditBaseForm(BaseForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    email = EmailField(_l('Email'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(UserEditBaseForm, self).__init__(*args, **kwargs)
        self._user = kwargs['obj']

    def validate_email(self, field):
        email = field.data.lower()
        if email != self._user.email:
            user = User.query.filter_by(email=email).first()
            if user:
                raise StopValidation(_l('Email has been registered.'))

    def edit(self, user):
        user.name = self.name.data
        user.email = self.email.data.lower()
        with db.auto_commit():
            db.session.add(user)
        return user


class UserEditPasswordForm(BaseForm):
    old_password = PasswordField(_l('Old password'), validators=[DataRequired()])
    new_password = PasswordField(_l('New password'), validators=[DataRequired()])

    def edit(self, user):
        old_password = self.old_password.data
        new_password = self.new_password.data
        if user.check_password(old_password):
            user.password = new_password
        with db.auto_commit():
            db.session.add(user)
        return user


class UserEditImageForm(BaseForm):
    avatar = FileField(_l('Avatar'),
                       render_kw={'accept': 'image/png, image/jpeg, image/jpg', 'onchange': 'loadImage(this)'})
    hidden_img = HiddenField(validators=[DataRequired()])

    def edit(self, user):
        with db.auto_commit():
            if user.image_filename and os.path.isfile(user.image_filename):
                os.remove(user.image_filename)
            user.image_filename = save_image(self.hidden_img.data)
            db.session.add(user)
        return user


class UserEditAccessTypeForm(BaseForm):
    email = EmailField(_l('Email'), validators=[DataRequired()])

    _user = None

    def validate_email(self, field):
        email = field.data.lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            raise StopValidation(_l("Email hasn't been found."))
        self._user = user

    def edit(self, user):
        with db.auto_commit():
            if self._user and user.email != self._user.email:
                if self._user.access_type == 'user':
                    self._user.access_type = 'admin'
                elif self._user.access_type == 'admin':
                    self._user.access_type = 'user'
                db.session.add(self._user)
        return user


class ResetPasswordRequestForm(BaseForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])

    _user = None

    def validate_email(self, field):
        email = field.data.lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            raise StopValidation(_l("Email hasn't been found."))
        self._user = user

    def request(self):
        send_password_reset_email(self._user)


class ResetPasswordForm(BaseForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])

    def reset(self, user):
        user.password = self.password.data
        with db.auto_commit():
            db.session.add(user)
