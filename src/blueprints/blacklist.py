import logging
import os

from flask import Blueprint, request, jsonify, Flask
from src.commands.block_email import AddEmailToBlackList
from src.commands.get_blocked_info import IsBlockedEmail
from src.commands.reset_database import ResetDatabase
from src.errors.errors import InvalidParams, UserAlreadyExists

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)
blacklist_blueprint = Blueprint('blacklist', __name__)


@blacklist_blueprint.route('/blacklist', methods=['POST'])
def add_email_to_blacklist():
    auth_header = request.headers.get('Authorization')
    parts = auth_header.split()
    if len(parts) != 2 or parts[0] != 'Bearer':
        return '', 403

    token = parts[1]
    if token != os.getenv('SECRET_TOKEN'):
        return '', 401

    try:
        data = request.get_json()

        add_email_to_blacklist_command = AddEmailToBlackList(
            data.get('email'),
            data.get('app_uuid'),
            data.get('blocked_reason'),
            request.remote_addr,
        ).execute()
        return jsonify(add_email_to_blacklist_command), 201
    except InvalidParams:
        return '', 400
    except UserAlreadyExists:
        return '', 412
    except Exception as e:
        return str(e), 400


@blacklist_blueprint.route('/blacklist/<string:email>', methods=['GET'])
def get_blocked_info(email):
    auth_header = request.headers.get('Authorization')
    parts = auth_header.split()
    if len(parts) != 2 or parts[0] != 'Bearer':
        return '', 403

    token = parts[1]
    if token != os.getenv('SECRET_TOKEN'):
        return '', 401

    try:
        blocked_info = IsBlockedEmail(email).execute()
        return jsonify(blocked_info), 200
    except InvalidParams:
        return '', 400
    except Exception as e:
        return str(e), 400


@blacklist_blueprint.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200


@blacklist_blueprint.route('/users/reset', methods=['POST'])
def reset_database():
    result = ResetDatabase().execute()
    return jsonify(result), 200
