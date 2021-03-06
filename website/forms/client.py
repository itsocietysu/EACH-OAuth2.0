from wtforms.fields import (
    StringField,
    TextAreaField,
    BooleanField,
    SelectMultipleField
)
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired
from werkzeug.security import gen_salt
from .base import BaseForm
from ..services.oauth2 import scopes
from ..models import db, OAuth2Client

from flask_babel import lazy_gettext as _l

SCOPES = [(k, k) for k in scopes]
GRANTS = [
    ('authorization_code', 'Authorization Code'),
    ('implicit', 'Implicit'),
    ('password', 'Password'),
    ('client_credentials', 'Client Credentials')
]


class OAuth2ClientWrapper(object):
    def __init__(self, client):
        self._client = client
        self.name = client.name
        self.website = client.website
        self.is_confidential = client.is_confidential
        self.redirect_uris = client.redirect_uris
        self.default_redirect_uri = client.default_redirect_uri
        self.allowed_scopes = client.allowed_scopes.split()
        self.allowed_grants = client.allowed_grants.split()


class Client2Form(BaseForm):
    name = StringField(_l('Client name'), validators=[DataRequired()])
    website = URLField(_l('Website'))
    is_confidential = BooleanField(_l('Confidential Client'))
    redirect_uris = TextAreaField(_l('Redirect URIs'))
    default_redirect_uri = URLField(_l('Default redirect URI'))
    allowed_scopes = SelectMultipleField(_l('Allowed scopes'), choices=SCOPES)
    allowed_grants = SelectMultipleField(_l('Allowed grants'), choices=GRANTS)

    def update(self, client):
        client.name = self.name.data
        client.website = self.website.data
        client.is_confidential = self.is_confidential.data
        client.redirect_uris = self.redirect_uris.data
        client.default_redirect_uri = self.default_redirect_uri.data
        client.allowed_scopes = ' '.join(self.allowed_scopes.data)
        client.allowed_grants = ' '.join(self.allowed_grants.data)
        with db.auto_commit():
            db.session.add(client)
        return client

    def save(self, user):
        name = self.name.data
        is_confidential = self.is_confidential.data

        client_id = gen_salt(48)
        if is_confidential:
            client_secret = gen_salt(78)
        else:
            client_secret = ''

        client = OAuth2Client(
            user_id=user.id,
            client_id=client_id,
            client_secret=client_secret,
            name=name,
            is_confidential=is_confidential,
            default_redirect_uri=self.default_redirect_uri.data,
            website=self.website.data,
            allowed_scopes=' '.join(self.allowed_scopes.data),
            allowed_grants=' '.join(self.allowed_grants.data),
        )
        with db.auto_commit():
            db.session.add(client)
        return client
