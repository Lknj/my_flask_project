from flask import Blueprint

profile_blue = Blueprint('profile_file', __name__, url_prefix='/user')

from . import view