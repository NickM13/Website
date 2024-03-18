# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, UserMixin, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, DateField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import validators
from .app import db, login_manager

# Create a Blueprint named 'auth'
auth = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	riot_id = db.Column(db.String(80), unique=True)
	password_hash = db.Column(db.String(120), nullable=False)
	is_admin = db.Column(db.Boolean, default=False)

	def get_riot_id_for_url(self):
		return self.riot_id.replace("#", "%23") if self.riot_id is not None else "None"


@auth.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user_exists = User.query.filter_by(username=username).first()

		if user_exists:
			flash('Username already exists.')
			return redirect(url_for('auth.register'))

		new_user = User(username=username, password_hash=generate_password_hash(password))
		db.session.add(new_user)
		db.session.commit()

		flash('User registered successfully!')
		return redirect(url_for('auth.login'))
	return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()

		if user and check_password_hash(user.password_hash, password):
			session['username'] = username
			flash('Logged in successfully!')
			login_user(user)
			return redirect(url_for('home'))
		flash('Invalid username or password')
	return render_template('login.html')


@auth.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


class EditProfileForm(FlaskForm):
	username = StringField('Username', render_kw={'readonly': True})
	riot_id = StringField('Riot ID', validators=[validators.Regexp('^[a-zA-Z0-9._]{3,16}#[0-9a-zA-Z]{3,5}$', message="This is your Riot ID, e.g TheNickMead#NA1")])
	submit = SubmitField('Update')


@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	user_id = request.args.get("user")
	if user_id:
		if current_user.is_admin:
			user = User.query.filter_by(username=user_id).first()
			if not user:
				flash(f"User does not exist: {user_id}", 'danger')
				return redirect(url_for("auth.edit_profile"))
		else:
			flash(f"You don't have permission to edit other user profiles", 'danger')
			return redirect(url_for("auth.edit_profile"))
	else:
		user = current_user

	if form.validate_on_submit():
		user.riot_id = form.riot_id.data
		db.session.commit()
		flash('Profile updated!', 'success')
		return redirect(url_for('home'))
	elif request.method == 'GET':
		form.username.data = user.username
		form.riot_id.data = user.riot_id

	print(form.errors)
	return render_template('edit_profile.html', title='Edit Profile', form=form)
