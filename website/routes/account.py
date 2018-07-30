from flask import Blueprint
from flask import url_for, redirect, render_template
from ..auth import current_user, logout as _logout
from ..forms.user import AuthenticateForm, UserCreationForm

from oauth2 import current_url
from flask import request

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
