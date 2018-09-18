from flask import Blueprint
from flask import send_file

bp = Blueprint('images', __name__)


@bp.route('/<image_file>', methods=['GET'])
def image(image_file):
    return send_file('../images/%s' % image_file)
