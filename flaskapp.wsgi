#!/usr/bin/python

import sys
import logging


sys.path.insert(0, "/var/www/FlaskApp/FlaskApp/")
#sys.path.insert(0, "/var/www/FlaskApp/FlaskApp/venv/lib/python3.8/site-packages")


from app import app as application

application.secret_key = "I'm not really sure what this is for"
