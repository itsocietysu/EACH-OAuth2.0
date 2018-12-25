from wtforms.fields import (
    PasswordField,
    BooleanField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from wtforms.validators import StopValidation
from .base import BaseForm
from ..models import User
from ..auth import login

from flask_babel import lazy_gettext as _l


class ConfirmForm(BaseForm):
    confirm = BooleanField(_l('Confirm'))


class LoginConfirmForm(ConfirmForm):
    email = EmailField(_l('Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])

    def validate_password(self, field):
        email = self.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(field.data):
            raise StopValidation(_l('Email or password is invalid.'))

        if self.confirm.data:
            login(user, False)
