from flask import render_template, Blueprint, redirect

website_bp = Blueprint('website', __name__)


@website_bp.route('/')
def default():
    return redirect("/login")


@website_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@website_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template("signup.html")


@website_bp.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@website_bp.route('/profile', methods=['GET'])
def profile():
    return render_template("profile.html")


@website_bp.route('/logout')
def logout():
    return render_template("login.html")
