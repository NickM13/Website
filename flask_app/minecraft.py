from sqlalchemy.ext.hybrid import hybrid_property
from wtforms.fields.simple import BooleanField

from .app import db, riot_watcher
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateTimeField, DateField
from wtforms.validators import DataRequired
import time
import datetime
import math
from .app import lol_watcher
from .auth import User
import io
import os

minecraft = Blueprint('minecraft', __name__)
log_filename = "~/LiveServer/logs/latest.log"

os.getenv("MC_LOGS")


@minecraft.route('/logs')
def logs():
	try:
		with io.open(log_filename, mode='r', encoding="utf-8") as f:
			text = f.read()
			return render_template('minecraft_logs.html', text=text)
	except:
		flash(f"No logs found: {log_filename}", 'danger')
		return redirect(url_for('home'))
