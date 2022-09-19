import os
import time
from urllib.parse import urljoin, urlparse

from dotenv import load_dotenv
from flask import (Flask, Response, abort, flash, redirect, render_template,
                   request, send_from_directory, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import IMAGES, UploadSet, configure_uploads
from pygtail import Pygtail
from werkzeug.utils import secure_filename

import database
import servers
from forms import AddServerForm, LoginForm, ProfileForm, RegistrationForm
from user import get_by_username, register_new_user, update_profile

load_dotenv("/var/www/FlaskApp/FlaskApp/.env")

app = Flask(__name__)
database.init()
app.secret_key = b'_5#y2L"F4P8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@localhost/website' % (
    os.environ.get("DBUSER"), os.environ.get("DBPASS"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_IMAGES_DEST'] = "uploads/images"
app.config['UPLOAD_FOLDER'] = "/var/www/FlaskApp/FlaskApp/static/uploads"
ALLOWED_EXTENTIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

LOG_FILE = '/var/www/FlaskApp/FlaskApp/logs/app.log'
# log = logging.getLogger('__name__')
# logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route("/api/v1/servers/", methods=["GET"])
def api_v1_servers():
    return str(servers.get_all_servers())


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENTIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.config["UPLOAD_FOLDER"], 'images'), filename)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_IMAGE_FOLDER"], filename))
            return redirect(url_for("uploaded_file", filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/notfound")
def not_found():
    return render_template("notfound.html")


@app.route("/logs")
def logs():
    return render_template("log.html")


@app.route('/log')
def progress_log():
	def generate():
		for line in Pygtail(LOG_FILE, every_n=1):
			yield "data:" + str(line) + "\n\n"
			time.sleep(0.01)
	return Response(generate(), mimetype= 'text/event-stream')


@app.route("/servers")
def server_list():
    serverlist = servers.get_all_servers()

    return render_template("servers.html", serverlist=serverlist)


@app.route("/server/info")
def server_info():
    server = request.args.get("server")
    if server is None:
        return not_found()
    return render_template("server_info.html", server=servers.get_server(server))


@app.route("/user/<user>")
def user_info(user: str):
    return render_template("user_info.html", user=get_by_username(user))


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
        picture = None
        if request.files['picture']:
            filename = request.files['picture'].filename
            if allowed_file(filename):
                rel_path = os.path.join("images")
                path = os.path.join(app.config['UPLOAD_FOLDER'], rel_path)
                os.makedirs(path, exist_ok = True)
                full_path = os.path.join(path, filename)
                request.files['picture'].save(full_path)
                picture = os.path.join(rel_path, filename)
                flash(full_path)
                flash(picture)
        
        res = update_profile(
            user=curr_user,
            display_name=form.display_name.data,
            email=form.email.data,
            discord=form.discord.data,
            picture=picture)

        if res == 0:
            flash("Didn't change anything.")
        elif res == 1:
            flash("Profile updated.")

        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('index'))
    else:
        form.display_name.data = curr_user.display_name
        form.email.data = curr_user.email
        form.discord.data = curr_user.discord
        form.picture.data = curr_user.picture

    return render_template('profile.html', form=form)


@app.route("/logout")
@login_required
def logout():
    flash("Logged out.")

    logout_user()

    next = request.args.get('next')
    if not is_safe_url(next):
        return abort(400)

    return redirect(next or url_for('index'))


@app.route("/test")
def test():
    return render_template('test.html')


@app.route("/servers/add", methods=["GET", "POST"])
@login_required
def server_add():
    form = AddServerForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        servers.add_server(form.game.data, name=form.name.data, ip=form.ip.data, owner=current_user.get_id(
        ), description=form.description.data, modinfo=form.modinfo.data)

        flash('Server added.')

        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('index'))
    return render_template('server_add.html', form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('register.html', form=form)

        user = register_new_user(username=form.username.data,
                                 password=form.password.data,
                                 email=form.email.data,
                                 display_name=form.display_name.data,
                                 discord=form.discord.data)

        login_user(user)
        flash('Account registered.')

        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('index'))

    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        next = request.form.get('next')
        user = form.user

        login_user(user, remember=True)

        flash("Welcome, %s." % (user.username))

        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return get_by_username(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    if request.path != '/logout':
        return redirect("/login?next=" + request.path)
    return redirect("/login")


if __name__ == "__main__":
    app.run()
