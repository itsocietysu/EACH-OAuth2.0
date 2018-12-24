import os

from flask_babel import Babel, request

from website import create_app
from website.models import db

is_dev = bool(os.getenv('FLASK_DEBUG'))

if is_dev:
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = 'true'
    conf_file = os.path.abspath('conf/dev.config.py')
    app = create_app(conf_file)
    babel = Babel(app)

    @app.after_request
    def add_header(resp):
        resp.headers['Cache-Control'] = 'no-store'
        resp.headers['Pragma'] = 'no-cache'
        return resp
else:
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = 'true'
    conf_file = os.path.abspath('conf/dev.config.py')
    app = create_app(conf_file)
    babel = Babel(app)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@app.cli.command()
def initdb():
    db.create_all()
