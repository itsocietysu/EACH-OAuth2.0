from flask import Blueprint, request
from flask import jsonify, render_template
from authlib.specs.rfc6749 import OAuth2Error
from authlib.flask.oauth2 import current_token
from ..models import OAuth2Client, OAuth2Token, User
from ..auth import current_user
from ..forms.auth import ConfirmForm, LoginConfirmForm
from ..services.oauth2 import authorization, scopes, require_oauth

from flask_cors import CORS

curr_url = None


def current_url():
    global curr_url
    return curr_url


bp = Blueprint('oauth2', __name__)
CORS(bp)


@bp.route('/authorize', methods=['GET', 'POST'])
def authorize():
    global curr_url
    curr_url = '/oauth2/authorize?' + request.query_string

    if current_user:
        form = ConfirmForm()
    else:
        form = LoginConfirmForm()

    if form.validate_on_submit():
        if form.confirm.data:
            # granted by current user
            grant_user = current_user
        else:
            grant_user = None
        return authorization.create_authorization_response(grant_user)
    try:
        grant = authorization.validate_authorization_request()
    except OAuth2Error as error:
        # TODO: add an error page
        payload = dict(error.get_body())
        return jsonify(payload), error.status_code

    client = OAuth2Client.get_by_client_id(request.args['client_id'])
    return render_template(
        'account/authorize.html',
        grant=grant,
        scopes=scopes,
        client=client,
        form=form,
    )


@bp.route('/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()


@bp.route('/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_revocation_response()


@bp.route('/revoke_bearer', methods=['POST'])
def revoke_token_bearer():
    token = OAuth2Token.query_token(request.form['access_token'])
    if token:
        token.revoke()
        return jsonify(token)
    return jsonify({'error': 'invalid token supplied'}), 401


@bp.route('/tokeninfo', methods=['GET'])
def get_token_info():
    token = OAuth2Token.query_token(request.args['access_token'])
    print(token)
    if token and token.user_id:
        user = User.query.get(token.user_id)
        print(user)
        udict = user.to_dict()
        udict.update(token.to_dict())
        return jsonify(udict)
    return jsonify({'error': 'invalid token supplied'}), 401
