#!/usr/bin/python

import sys
import logging


sys.path.insert(0, "/var/www/Website")
sys.path.insert(0, "/var/www/Website/venv/lib/python3.8/site-packages")


from app import app as application

application.secret_key = "Ilkaehstolihdszfvik;ljfdslikxkyhf"
