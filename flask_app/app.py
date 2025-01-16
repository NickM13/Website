from flask import Flask, session, redirect, url_for, render_template
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from riotwatcher import LolWatcher, RiotWatcher
from flask_login import LoginManager
from flask_migrate import Migrate

import os

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET']
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

db = SQLAlchemy(app, metadata=metadata)
bcrypt = Bcrypt()
lol_watcher = LolWatcher(os.environ['RIOT_API_KEY'])
riot_watcher = RiotWatcher(os.environ['RIOT_API_KEY'])
login_manager = LoginManager()

from .valorant import ValorantGuess, ValorantEvent, ValorantEventParticipants
from .league import Summoner, ChampionMastery, Match, MatchInfo, MatchMetadata
from .auth import User

migrate = Migrate(app, db, render_as_batch=True)


@app.context_processor
def inject_league_version():
	return dict(league_version="14.6.1")


@app.route('/')
def home():
	return render_template('index.html')


def create_app():
	bcrypt.init_app(app)
	login_manager.init_app(app)
	login_manager.login_view = 'auth.login'

	from .auth import auth
	from .valorant import val
	from .league import league
	from .minecraft import minecraft

	with app.app_context():
		db.create_all()

	# flask_app.register_blueprint(main)
	app.register_blueprint(auth, url_prefix='/')
	app.register_blueprint(val, url_prefix='/val')
	app.register_blueprint(league, url_prefix='/league')
	app.register_blueprint(minecraft, url_prefix='/minecraft')

	return app
