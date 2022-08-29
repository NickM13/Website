import flask
from flask import Flask, render_template, request, url_for
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from forms import AddServerForm, RegistrationForm, LoginForm, ProfileForm
from urllib.parse import urlparse, urljoin
from user import get_by_username, register_new_user, update_profile
import servers
import database
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4P8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@localhost/website' % (os.getenv("dbuser"), os.getenv("dbpasswd"))

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/servers")
def server_list():
    serverlist = servers.get_servers()

    return render_template("servers.html", serverlist=serverlist)


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    curr_user = get_by_username(current_user.get_id())

    form = ProfileForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        res = update_profile(
            curr_user, form.display_name.data, form.email.data)

        if res == 0:
            flask.flash("Didn't change anything.")
        elif res == 1:
            flask.flash("Profile updated.")

        next = flask.request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or url_for('index'))
    else:
        form.display_name.data = curr_user.display_name
        form.email.data = curr_user.email

    return flask.render_template('profile.html', form=form)


@app.route("/logout")
@login_required
def logout():
    flask.flash("Goodbye, %s ☺" % current_user.username)

    logout_user()

    next = flask.request.args.get('next')
    if not is_safe_url(next):
        return flask.abort(400)

    return flask.redirect(next or url_for('index'))


# @app.route("/test")
@login_required
def test():
    res = database.execute(
        "insert into servers (game, name, ip, owner, description, modinfo, created) values ('Minecraft', 'ST1', 'localhost', 'nickm13', '...', '', current_timestamp)")
    flask.flash("test")
    flask.flash(res)
    return flask.render_template('home.html')


@app.route("/servers/add", methods=["GET", "POST"])
@login_required
def server_add():
    form = AddServerForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        servers.add_server(form.game.data, name=form.name.data, ip=form.ip.data, owner=current_user.get_id(
        ), description=form.description.data, modinfo=form.modinfo.data)

        flask.flash('Server added.')

        next = flask.request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or url_for('index'))
    return flask.render_template('server_add.html', form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            for i in form.errors:
                flask.flash(i)
            return flask.render_template('register.html', form=form)

        user = register_new_user(username=form.username.data,
                                 password=form.password.data,
                                 email=form.email.data,
                                 display_name=form.display_name.data)

        login_user(user)
        flask.flash('Account registered.')

        next = flask.request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or url_for('index'))
        
    return flask.render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user = form.user

        login_user(user, remember=True)

        flask.flash("Welcome, %s." % user.username)

        next = flask.request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or url_for('index'))
    return flask.render_template('login.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return get_by_username(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return "You don't have permission to do that!"


if __name__ == "__main__":
    app.run()
