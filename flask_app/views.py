from flask import Blueprint, render_template, request, flash, redirect, url_for
from .app import db, bcrypt
from .models import Summoner, ChampionMastery, Match
from .extensions import get_summoner_by_name, insert_matches, insert_champion_masteries, get_latest_matches, insert_match
from .app import lol_watcher
import requests
from PIL import Image
import io

main = Blueprint('main', __name__)


def fetch_png(url):
	response = requests.get(url)
	image = Image.open(io.BytesIO(response.content))
	image = image.convert('RGBA')  # Ensure we have RGBA data

	width, height = image.size
	pixels = list(image.getdata())

	flat_pixels = [channel for pixel in pixels for channel in pixel]

	return {
		"width": width,
		"height": height,
		"pixels": flat_pixels
	}


def fetch_png_file(file_path):
	"""
    Reads a PNG from a local file path and returns its width, height, and pixel data.

    Args:
    - file_path (str): The path to the local PNG file.

    Returns:
    - Dictionary with the width, height, and pixel data.
    """
	file_path = "C:/Users/NickM/Documents/Python Projects/Website/flask_app/static/" + file_path
	with Image.open(file_path) as img:
		pixels = list(img.getdata())
		width, height = img.size

	flat_pixels = [channel for pixel in pixels for channel in pixel]

	return {
		"width": width,
		"height": height,
		"pixels": pixels
	}


@main.route('/')
def index():
	return render_template('index.html')


@main.route('/league/match/add', methods=['GET', 'POST'])
def league_match_add():
	if request.method == 'POST':
		match_id = request.form.get('match_id')
		if match_id:
			insert_match(match_id)
			return "Match with ID {} has been inserted.".format(match_id)

	return render_template('match_add.html')


@main.route('/showall')
def show_all():
	return render_template('show_all.html', matches=Match.query.all())


@main.route('/history/<string:name>')
def history(name):
	summoner = get_summoner_by_name(name)
	#matches = insert_matches(summoner)
	matches = get_latest_matches(summoner)
	return render_template('match_history.html', summoner=summoner, matches=matches)


@main.route('/all/history')
def all_history():
	summoner = get_summoner_by_name('TheNickMead')
	matches = Match.query.all()
	return render_template('match_history.html', summoner=summoner, matches=matches)


@main.route('/match_info', methods=['GET', 'POST'])
def match_info():
	match_id = request.args.get('match_id')

	if match_id is not None:
		match_data = lol_watcher.match.by_id(match_id)
		print(match_data)
		return render_template('match_info.html', match_data=match_data)

	return render_template('match_info.html')


@main.route('/model/converter/convert', methods=['GET', 'POST'])
def model_converter_convert():
	if 'file' not in request.files:
		print('No file found')
	else:
		print(request.files['file'])
	return render_template('nvm_converter.html')


@main.route('/league/champion/scouter', methods=['GET', 'POST'])
def champ_scouter():
	region = request.args.get('region')
	summoner_name = request.args.get('summoner')

	if region and summoner_name:
		summoner = get_summoner_by_name(summoner_name, region)

		if summoner:
			champions = insert_champion_masteries(summoner)
			print(champions)
			return render_template('champion_scouter.html', summoner=summoner, champions=champions)

	return render_template('champion_scouter.html')


@main.route('/nvm/converter')
def nvm_converter():
	return render_template('nvm_converter.html')


@main.route('/dnd/build/<string:class_name>', methods=['GET', 'POST'])
def dnd_build(class_name):

	return render_template('dnd_build.html', class_name=class_name)
