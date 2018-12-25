from flask import Blueprint, jsonify, abort
from flask import url_for, redirect, render_template

from website.models import OAuth2Token, User
from ..auth import current_user, logout as _logout
from ..forms.user import AuthenticateForm, UserCreationForm, UserEditBaseForm, UserEditPasswordForm, \
    UserEditImageForm, UserEditAccessTypeForm

from oauth2 import current_url
from flask import request

import json

bp = Blueprint('account', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user:
        return redirect(url_for('front.home'))
    form = AuthenticateForm()
    if form.validate_on_submit():
        form.login()
        return redirect(url_for('front.home'))
    return render_template('account/login.html', form=form)


@bp.route('/logout')
def logout():
    _logout()
    return redirect(url_for('front.home'))


urls = []


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    global urls
    if current_user:
        return redirect(request.referrer)
    form = UserCreationForm()
    if form.validate_on_submit():
        form.signup()
        tmp = urls[0]
        del urls
        urls = []
        if 'authorize' in tmp:
            return redirect(tmp)
        else:
            return redirect(url_for('front.home'))
    urls.append(request.referrer)
    return render_template('account/signup.html', form=form)


@bp.route('/edit', methods=['GET'])
def edit():
    if not current_user:
        return redirect(request.referrer)
    return render_template('account/edit.html')


@bp.route('/edit/base', methods=['GET', 'POST'])
def edit_base():
    if not current_user:
        return redirect(request.referrer)
    form = UserEditBaseForm(obj=current_user)
    if form.validate_on_submit():
        form.edit(current_user)
        return redirect(url_for('front.home'))
    return render_template('account/edit_base.html', form=form)


@bp.route('/edit/password', methods=['GET', 'POST'])
def edit_password():
    if not current_user:
        return redirect(request.referrer)
    form = UserEditPasswordForm()
    if form.validate_on_submit():
        form.edit(current_user)
        return redirect(url_for('front.home'))
    return render_template('account/edit_base.html', form=form)


@bp.route('/edit/image', methods=['GET', 'POST'])
def edit_image():
    if not current_user:
        return redirect(request.referrer)
    form = UserEditImageForm()
    if form.validate_on_submit():
        form.edit(current_user)
        return redirect(url_for('front.home'))
    return render_template('account/edit_image.html', form=form)


@bp.route('/edit/access_type', methods=['GET', 'POST'])
def edit_access_type():
    if not current_user:
        return redirect(request.referrer)
    if current_user.access_type == 'admin':
        form = UserEditAccessTypeForm()
        if form.validate_on_submit():
            form.edit(current_user)
            return redirect(url_for('front.home'))
        return render_template('account/edit_base.html', form=form)
    else:
        abort(404)


@bp.route('/update', methods=['POST'])
def update_user():
    authorization = request.headers.get('authorization')
    if authorization:
        auth = authorization.split(" ")
        if len(auth) < 2 or auth[0].lower() != 'bearer':
            return jsonify({'error': 'Token was not provided in schema [bearer <Token>]'}), 401
        access_token = authorization.split(" ")[1].strip()
    else:
        return jsonify({'error': 'Token was not provided in schema [bearer <Token>]'}), 401

    token = OAuth2Token.query_token(access_token)
    if not token:
        return jsonify({'error': 'Invalid token supplied'}), 401

    try:
        data = json.loads(request.data)
        user = User.update(token.user_id, data)

        if not user:
            return jsonify({'error': "User wasn't found"}), 500
        udict = user.to_dict(request.host)
        return jsonify(udict)
    except ValueError:
        return jsonify({'error': 'Invalid parameters supplied.'}), 400


