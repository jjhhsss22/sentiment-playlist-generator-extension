from flask import render_template, Blueprint

website_bp = Blueprint('website', __name__)


@website_bp.route('/', defaults={'path': ''})
@website_bp.route('/<path:path>')
def index(path):
    return render_template("index.html")
