import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreateLoginForm, CreateUserForm

# initialize the flask app
app = Flask(__name__)
# set a secret key for use with the flask app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# initialize the flask application with bootstrap
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# set up flask_login with the flask application
login_manager = LoginManager()
login_manager.init_app(app)


# This class represents the User table in the shop database
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))


# create the database if it does not exists
db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# a route to the home page
@app.route("/")
def home():
    """
    This method is called when the home route is loaded on the web browser. It renders the home page
    :return: (str) the web page is rendered
    """
    return render_template("index.html", logged_in=current_user.is_authenticated)


# a route to the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    This method logs in the user to the application
    :return: (str) the login.html page
    """

    # the form where the user will type its credentials
    form = CreateLoginForm()

    # if the form has been submitted and validated
    if form.validate_on_submit():
        # check if a user with the email exists
        user = User.query.filter_by(email=form.email.data).first()
        # if a user exists, login in the user
        if user:
            password = form.password.data
            if check_password_hash(pwhash=user.password, password=password):
                login_user(user=user)
                return redirect(url_for("home"))

            # if the password doesn't match
            flash("Password doesn't match")
            return redirect(url_for("login"))

        # if the email doesn't exist
        flash("Email doesn't exist")
        return redirect(url_for("login"))

    # render the login page
    return render_template("login.html", form=form)


# a route to the register web page
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    This method allows a user to create an account
    :return: (str) the register.html page
    """

    # the form where the user will type its information
    form = CreateUserForm()

    # if the form has been submitted and validated
    if form.validate_on_submit():

        # check if the user with the email already exist
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        # if it doesn't register the new user
        if not user:
            new_user = User(email=email, password=generate_password_hash(password=form.password.data, salt_length=8),
                            name=form.name.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("home"))

        # if the email exist redirect the user
        flash("Email Already Exists")
        return redirect(url_for("login"))

    # return the register.html page
    return render_template("register.html", form=form)


# a route to the shop web page
@app.route("/shop")
@login_required
def shop():
    """
    This method returns the web page where all the goods are being sold
    :return: (str) glasses.html page
    """

    return render_template("glasses.html")


# a route to the about web page
@app.route("/about")
def about():
    """
    This method returns the about web page
    :return: (str) about.html page
    """
    return render_template("about.html", logged_in=current_user.is_authenticated)


# a route to the contact web page
@app.route("/contact")
def contact():
    """
    This method returns the contact web page
    :return: (str) contact.html page
    """

    return render_template("contact.html", logged_in=current_user.is_authenticated)


# a route to the logout web page
@app.route("/logout")
def logout():
    """
    This method logs out the current user
    :return:
    """
    logout_user()
    return redirect(url_for("home"))


# if this is the main app, run this application in debug mode
if __name__ == "__main__":
    app.run(debug=True)
