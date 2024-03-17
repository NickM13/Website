from flask import Flask, session, redirect, url_for, render_template
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from riotwatcher import LolWatcher
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'secret-key_nmead5'  # Needed for session management
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

login_manager = LoginManager()
db = SQLAlchemy(app, metadata=metadata)
bcrypt = Bcrypt()
lol_watcher = LolWatcher('RGAPI-828f8f23-348e-40ee-b84e-8be50c56070f')

from .models import Summoner, ChampionMastery, Match, MatchInfo, MatchMetadata
from .valorant import ValorantGuess, ValorantEvent, ValorantEventParticipants
from .auth import User

migrate = Migrate(app, db, render_as_batch=True)


@app.route('/')
def home():
	return render_template('index.html')


def create_app():
	bcrypt.init_app(app)
	login_manager.init_app(app)
	login_manager.login_view = 'auth.login'

	from .views import main
	from .auth import auth
	from .valorant import val

	# flask_app.register_blueprint(main)
	app.register_blueprint(auth, url_prefix='/')
	app.register_blueprint(val, url_prefix='/val')

	return app
