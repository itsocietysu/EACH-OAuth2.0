import base64
import re
import json

from wtforms.fields import StringField, PasswordField, HiddenField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from wtforms.validators import StopValidation
from .base import BaseForm
from ..models import db, User
from ..auth import login
from ..media_resolver.mediaresolverfactory import MediaResolverFactory


class AuthenticateForm(BaseForm):
    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(AuthenticateForm, self).__init__(*args, **kwargs)
        self._user = None

    def validate_password(self, field):
        email = self.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(field.data):
            raise StopValidation('Email or password is invalid.')
        self._user = user

    def login(self):
        if self._user:
            login(self._user, True)


def save_image(field):
    with open('website/def.image.json', 'r') as f:
        default_image = re.sub('data:image/(jpeg|png|jpg);base64,', '', json.load(f)['image'])
        f.close()
    if not field.data:
        resolver = MediaResolverFactory.produce('image', base64.b64decode(default_image))
        return resolver.resolve()
    value = re.sub('data:image/(jpeg|png|jpg);base64,', '', field.data)
    resolver = MediaResolverFactory.produce('image', base64.b64decode(value))
    return resolver.resolve()


class UserCreationForm(BaseForm):
    name = StringField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    image = FileField(render_kw={'accept': 'image/png, image/jpeg, image/jpg', 'onchange': 'loadImage(this)'})
    hidden_img = HiddenField()

    def validate_email(self, field):
        email = field.data.lower()
        user = User.query.filter_by(email=email).first()
        if user:
            raise StopValidation('Email has been registered.')

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
