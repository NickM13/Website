from flask import Blueprint, render_template, request, flash, redirect, url_for
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


@main.route('/model/converter/convert', methods=['GET', 'POST'])
def model_converter_convert():
	if 'file' not in request.files:
		print('No file found')
	else:
		print(request.files['file'])
	return render_template('nvm_converter.html')


@main.route('/nvm/converter')
def nvm_converter():
	return render_template('nvm_converter.html')


@main.route('/dnd/build/<string:class_name>', methods=['GET', 'POST'])
def dnd_build(class_name):

	return render_template('dnd_build.html', class_name=class_name)
