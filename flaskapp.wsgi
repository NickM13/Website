#!/usr/bin/python

import sys
import logging


logging.basicConfig(level=logging.DEBUG,
                    filename="/var/www/FlaskApp/FlaskApp/logs/latest.log",
                    format='%(asctime)s %(message)s')

sys.path.insert(0, "/var/www/FlaskApp/FlaskApp/")
#sys.path.insert(0, "/var/www/FlaskApp/FlaskApp/venv/lib/python3.8/site-packages")


from app import app as application

application.secret_key = "I'm not really sure what this is for"
