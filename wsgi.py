import sys

sys.stdout = sys.stderr
sys.path.insert(0, "/home/azureuser/Website")

from flask_app.app import create_app

application = create_app()

if __name__ == "__main__":
    application.run(debug=True)
