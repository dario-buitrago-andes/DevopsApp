import logging
from flask import Blueprint, jsonify, request
from src.commands.block_email import AddEmailToBlackList
from src.commands.get_blocked_info import IsBlockedEmail
from src.commands.reset_database import ResetDatabase
from src.errors.errors import InvalidParams, UserAlreadyExists
import newrelic.agent  

blacklist_blueprint = Blueprint('blacklist', __name__)

@blacklist_blueprint.route('/', methods=['GET'])
def ping():
    newrelic.agent.record_custom_event('PingEndpoint', {
        'status': 'success'
    })
    return "pong", 200

@blacklist_blueprint.route('/users/reset', methods=['POST'])
def reset_database():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer ") or auth_header.split()[1] != "valid_token":
        newrelic.agent.record_custom_event('ResetDatabase', {
            'result': 'unauthorized'
        })
        return jsonify({"error": "Unauthorized"}), 403

    try:
        result = ResetDatabase().execute()
        newrelic.agent.record_custom_event('ResetDatabase', {
            'result': 'success'
        })
        return jsonify(result), 200
    except Exception as e:
        newrelic.agent.record_custom_event('ResetDatabase', {
            'result': 'error',
            'error_message': str(e)
        })
        return jsonify({"error": str(e)}), 500

@blacklist_blueprint.route('/blacklist', methods=['POST'])
def add_email_to_blacklist():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer ") or auth_header.split()[1] != "valid_token":
        newrelic.agent.record_custom_event('AddEmailToBlacklist', {
            'result': 'unauthorized'
        })
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.get_json()
        add_email_to_blacklist_command = AddEmailToBlackList(
            data.get('email'),
            data.get('app_uuid'),
            data.get('blocked_reason'),
            request.remote_addr,
        ).execute()
        newrelic.agent.record_custom_event('AddEmailToBlacklist', {
            'email': data.get('email'),
            'result': 'success'
        })
        return jsonify(add_email_to_blacklist_command), 201
    except InvalidParams:
        newrelic.agent.record_custom_event('AddEmailToBlacklist', {
            'email': data.get('email'),
            'result': 'invalid_params'
        })
        return jsonify({"error": "Invalid parameters"}), 400
    except UserAlreadyExists:
        newrelic.agent.record_custom_event('AddEmailToBlacklist', {
            'email': data.get('email'),
            'result': 'user_exists'
        })
        return jsonify({"error": "User already exists"}), 412
    except Exception as e:
        newrelic.agent.record_custom_event('AddEmailToBlacklist', {
            'email': data.get('email'),
            'result': 'error',
            'error_message': str(e)
        })
        return jsonify({"error": str(e)}), 500

@blacklist_blueprint.route('/blacklist/<string:email>', methods=['GET'])
def get_blocked_info(email):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        newrelic.agent.record_custom_event('GetBlockedInfo', {
            'email': email,
            'result': 'unauthorized'
        })
        return jsonify({"error": "Unauthorized"}), 403

    token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else None
    if token != "valid_token":
        newrelic.agent.record_custom_event('GetBlockedInfo', {
            'email': email,
            'result': 'unauthorized'
        })
        return jsonify({"error": "Unauthorized"}), 403

    try:
        blocked_info = IsBlockedEmail(email).execute()
        newrelic.agent.record_custom_event('GetBlockedInfo', {
            'email': email,
            'result': 'success',
            'is_blacklisted': blocked_info.get("blacklisted_email")
        })
        return jsonify(blocked_info), 200
    except InvalidParams:
        newrelic.agent.record_custom_event('GetBlockedInfo', {
            'email': email,
            'result': 'invalid_params'
        })
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        newrelic.agent.record_custom_event('GetBlockedInfo', {
            'email': email,
            'result': 'error',
            'error_message': str(e)
        })
        return jsonify({"error": str(e)}), 500
