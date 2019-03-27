from flask import Blueprint, request
from flask import jsonify, render_template
from authlib.specs.rfc6749 import OAuth2Error
from authlib.flask.oauth2 import current_token
from ..models import OAuth2Client, OAuth2Token, User
from ..auth import current_user
from ..forms.auth import ConfirmForm, LoginConfirmForm
from ..services.oauth2 import authorization, scopes, require_oauth
from urlparse import parse_qs

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
    print("OAUTH2: method oauth2/authorize")

    if current_user:
        print("OAUTH2: confirm form")
        form = ConfirmForm()
    else:
        print("OAUTH2: login confirm form")
        form = LoginConfirmForm()

    if form.validate_on_submit():
        print("OAUTH2: submit")
        if form.confirm.data:
            # granted by current user
            grant_user = current_user
        else:
            grant_user = None
        print("OAUTH2: calling lib function")
        return authorization.create_authorization_response(grant_user)
    try:
        print("OAUTH2: not submit")
        print("OAUTH2: calling lib function")
        grant = authorization.validate_authorization_request()
    except OAuth2Error as error:
        # TODO: add an error page
        payload = dict(error.get_body())
        return jsonify(payload), error.status_code

    client = OAuth2Client.get_by_client_id(request.args['client_id'])
    print("OAUTH2: render")
    return render_template(
        'account/authorize.html',
        grant=grant,
        scopes=scopes,
        client=client,
        form=form,
    )


@bp.route('/token', methods=['POST'])
def issue_token():
    print("OAUTH2: method oauth2/token")
    print("OAUTH2: calling lib function")
    return authorization.create_token_response()


@bp.route('/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_revocation_response()


@bp.route('/revoke_bearer', methods=['POST'])
def revoke_token_bearer():
    print("OAUTH2: method oauth2/revoke_bearer")
    print("OAUTH2: query token")
    token = OAuth2Token.query_token(parse_qs(request.query_string)['token'][0])
    if token:
        print("OAUTH2: revoke")
        token.revoke()
        print("OAUTH2: return")
        return jsonify(token)
    return jsonify({'error': 'Invalid token supplied'}), 401


@bp.route('/tokeninfo', methods=['GET'])
def get_token_info():
    print("OAUTH2: method oauth2/tokeninfo")
    if 'access_token' in request.args:
        print("OAUTH2: query token")
        token = OAuth2Token.query_token(request.args['access_token'])
        if token and token.user_id:
            print("OAUTH2: query user")
            user = User.query.get(token.user_id)
            udict = user.to_dict(request.host)
            udict.update(token.to_dict())
            print("OAUTH2: return user info")
            return jsonify(udict)
        return jsonify({'error': 'Invalid token supplied'}), 401
    return jsonify({'error': 'Invalid parameters supplied'}), 400


@bp.route('/emailinfo', methods=['GET'])
def get_email_info():
    print("OAUTH2: method oauth2/emailinfo")
    if 'email' in request.args and 'access_token' in request.args:
        print("OAUTH2: query token")
        token = OAuth2Token.query_token(request.args['access_token'])
        email = request.args['email']
        if token and token.user_id:
            print("OAUTH2: query user")
            user = User.query_email(email)
            if user:
                udict = user.to_dict(request.host)
                print("OAUTH2: return user info")
                return jsonify(udict)
            return jsonify({'error': 'Invalid email supplied'}), 404
        return jsonify({'error': 'Invalid token supplied'}), 401
    return jsonify({'error': 'Invalid parameters supplied'}), 400
