import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

print("FLASK_ENV ",os.getenv('FLASK_ENV'))
if os.getenv('FLASK_ENV') == 'development':
    env_path = os.path.join(parent_dir, '.env.development')
else:
    env_path = os.path.join(parent_dir, '.env.test')

loaded = load_dotenv(env_path)
if not loaded:
    print("No se cargaron las variables de entorno")

print("Variables de entorno cargadas correctamente ",env_path)

from flask import Flask, jsonify
from src.blueprints.blacklist import blacklist_blueprint
from src.errors.errors import ApiError

from src.database import init_db

application = Flask(__name__)
application.register_blueprint(blacklist_blueprint)

@application.errorhandler(ApiError)
def handle_exception(err):
    response = {
      "mssg": err.description,
      "version": os.environ["VERSION"]
    }
    return jsonify(response), err.code


init_db()

