from flask import Flask
from models import db


app = Flask(__name__)

# Load configuration from config.py
app.config.from_object('config.Config')

# Initialize the database with the app
db.init_app(app)


from routes import app as routes_app
app.register_blueprint(routes_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
