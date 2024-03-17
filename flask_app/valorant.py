from sqlalchemy.ext.hybrid import hybrid_property

from .app import db
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateTimeField, DateField
from wtforms.validators import DataRequired

from .auth import User

val = Blueprint('val', __name__)


class ValorantEvent(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	sign_up_end = db.Column(db.DateTime, default=datetime.utcnow)
	guess_end = db.Column(db.DateTime, default=(datetime.utcnow() + timedelta(days=7)))
	event_end = db.Column(db.DateTime, default=(datetime.utcnow() + timedelta(days=30)))
	participants = db.relationship('ValorantEventParticipants',
	                               backref=db.backref('valorant_events', lazy=True))

	@hybrid_property
	def is_signing_up(self):
		return datetime.utcnow() < self.sign_up_end

	@hybrid_property
	def is_guessing(self):
		return datetime.utcnow() < self.guess_end

	@hybrid_property
	def is_ongoing(self):
		return datetime.utcnow() < self.event_end

	@hybrid_property
	def is_finished(self):
		return datetime.utcnow() > self.event_end


class ValorantEventParticipants(db.Model):
	__tablename__ = 'valorant_event_participants'
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	event_id = db.Column(db.Integer, db.ForeignKey('valorant_event.id'), primary_key=True)
	guesses = db.relationship('ValorantGuess', backref='participant', lazy='dynamic')

	def get_user(self):
		return User.query.get(self.user_id)

	def get_guess(self, user):
		guess = (ValorantGuess.query
		         .filter(ValorantGuess.guesser_id == self.user_id)
		         .filter(ValorantGuess.event_id == self.event_id)
		         .filter(ValorantGuess.participant_id == user.user_id)
		         .first())
		return guess.get_rank() if guess else "No guess"


class ValorantGuess(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	guesser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	participant_id = db.Column(db.Integer, db.ForeignKey('valorant_event_participants.user_id'), nullable=False)
	rank_id = db.Column(db.Integer, db.ForeignKey('valorant_tier.id'))
	division_id = db.Column(db.Integer)
	event_id = db.Column(db.Integer, db.ForeignKey('valorant_event.id'))

	def get_rank(self):
		tier = ValorantTier.query.get(self.rank_id)
		division = f" {self.division_id}" if not tier.is_apex else ""
		return f"{tier.name}{division}"


# Iron, Gold, Immortal, ...
class ValorantTier(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	is_apex = db.Column(db.Boolean, default=False)
	order = db.Column(db.Integer, default=0)
	btn_color = db.Column(db.String(100), default="primary")


class AddEventForm(FlaskForm):
	name = StringField('Event Name', validators=[DataRequired()])
	sign_up_end = DateField('Sign-Up End Date', format='%Y-%m-%d',
	                        validators=[DataRequired()])
	guess_end = DateField('Guess End Date', format='%Y-%m-%d',
	                      validators=[DataRequired()])
	event_end = DateField('Event End Date', format='%Y-%m-%d',
	                      validators=[DataRequired()])
	submit = SubmitField('Create Event')


class EditEventForm(FlaskForm):
	id = IntegerField('Event Id', render_kw={'readonly': True})
	name = StringField('Event Name', validators=[DataRequired()])
	sign_up_end = DateField('Sign-Up End Date', format='%Y-%m-%d',
	                        validators=[DataRequired()])
	guess_end = DateField('Guess End Date', format='%Y-%m-%d',
	                      validators=[DataRequired()])
	event_end = DateField('Event End Date', format='%Y-%m-%d',
	                      validators=[DataRequired()])
	submit = SubmitField('Update Event')


@val.route('/')
def home():
	future_events = (ValorantEvent.query
	                 .filter(ValorantEvent.is_signing_up)
	                 .filter(~ValorantEvent.participants.any(user_id=current_user.get_id()))
	                 .all())

	events_to_guess = (ValorantEvent.query
	                   .filter(~ValorantEvent.is_signing_up)
	                   .filter(ValorantEvent.is_guessing)
	                   .filter(ValorantEvent.participants.any(user_id=current_user.id))
	                   .all())

	running_events = (ValorantEvent.query
	                  .filter(~ValorantEvent.is_guessing)
	                  .filter(ValorantEvent.is_ongoing)
	                  .filter(ValorantEvent.participants.any(user_id=current_user.id))
	                  .all())

	return render_template('valorant_home.html', future_events=future_events, events_to_guess=events_to_guess,
	                       running_events=running_events)


@val.route('/signup', methods=['GET', 'POST'])
@login_required
def event_signup():
	if request.method == 'POST':
		event_id = request.form.get('event_id')
		event = ValorantEvent.query.filter_by(id=event_id).first()

		if not event:
			flash('Invalid event.', 'danger')
			return redirect(url_for('event_signup'))

		# Check if the sign-up period is still open
		if event.sign_up_end < datetime.utcnow():
			flash('The sign-up period for this event has ended.', 'warning')
			return redirect(url_for('event_signup'))

		# Add the current user to the event's participants
		# Assuming a many-to-many relationship between users and events
		if current_user not in event.participants:
			event.participants.append(current_user)
			db.session.commit()
			flash('You have successfully signed up for the event!', 'success')
		else:
			flash('You are already signed up for this event.', 'info')

		return redirect(url_for('val.home'))  # Redirect to the homepage or dashboard

	# GET request: display the signup form with the list of events
	events = ValorantEvent.query.filter(ValorantEvent.sign_up_end > datetime.utcnow()).filter(
		~ValorantEvent.participants.any(id=current_user.get_id())).all()
	return render_template('valorant_event_signup.html', events=events)


@val.route('/view_event', methods=['GET', 'POST'])
@login_required
def view_event():
	event = ValorantEvent.query.get(request.args.get("event_id"))

	return render_template('valorant_view_event.html', event=event)


@val.route('/submit_guess', methods=['GET', 'POST'])
@login_required
def submit_guess():
	event_id = request.args.get('event_id')
	event = ValorantEvent.query.get(event_id)
	if request.method == 'POST':
		guesser = (ValorantEventParticipants.query
		           .join(User)
		           .join(ValorantEvent)
		           .filter(User.id == current_user.id)
		           .first())

		for key in request.form.keys():
			if "_rank" in key:
				guess_value = request.form.get(key)
				participant_id = key.split("_")[0]
				tier, division = guess_value.split("_")
				guess = (ValorantGuess.query
				         .filter(ValorantGuess.event_id == event_id)
				         .filter(ValorantGuess.guesser_id == current_user.id)
				         .first())
				if guess:
					guess.rank_id = int(tier)
					guess.division_id = int(division)
				else:
					guess = ValorantGuess(
						event_id=event.id,
						guesser_id=guesser.user_id,
						participant_id=participant_id,
						rank_id=int(tier),
						division_id=int(division)
					)
					guesser.guesses.add(guess)
					db.session.add(guess)

		db.session.commit()
		flash('Guesses submitted!')
		return redirect(url_for('home'))

	possible_ranks = ValorantTier.query.order_by(ValorantTier.order).all()

	return render_template('valorant_submit_guess.html', event=event, possible_ranks=possible_ranks)


@val.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
	# if not current_user.is_admin:
	#	return redirect(url_for('val.home'))

	form = AddEventForm()
	if form.validate_on_submit():
		event = ValorantEvent(
			name=form.name.data,
			sign_up_end=form.sign_up_end.data,
			event_end=form.event_end.data,
			guess_end=form.guess_end.data
		)
		db.session.add(event)
		db.session.commit()
		flash('Event has been created successfully!')
		return redirect(url_for('val.home'))

	return render_template('valorant_add_event.html', form=form)


@val.route('/edit_event', methods=['GET', 'POST'])
@login_required
def edit_event():
	# if not current_user.is_admin:
	#	return redirect(url_for('val.home'))

	event = ValorantEvent.query.get(request.args.get("event_id"))

	if not event:
		flash(f"No event with id {id} exists", 'fatal')
		return redirect(url_for('val.home'))

	form = EditEventForm()
	if form.validate_on_submit():
		event.name = form.name.data
		event.sign_up_end = form.sign_up_end.data
		event.guess_end = form.guess_end.data
		event.event_end = form.event_end.data
		db.session.commit()
		flash('Event updated', 'success')
		return redirect(url_for('val.home'))
	elif request.method == 'GET':
		form.name.data = event.name
		form.event_end.data = event.event_end
		form.guess_end.data = event.guess_end
		form.sign_up_end.data = event.sign_up_end

	return render_template('valorant_edit_event.html', form=form)
