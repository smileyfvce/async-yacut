from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config

app = Flask(__name__)
app.config.from_object(Config)
app.json.ensure_ascii = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from yacut import views
from yacut import error_handlers
from yacut import api_views