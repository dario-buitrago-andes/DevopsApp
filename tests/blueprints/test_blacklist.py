import pytest
from flask import Flask
from src.blueprints.blacklist import blacklist_blueprint
from src.commands.block_email import AddEmailToBlackList
from src.commands.get_blocked_info import IsBlockedEmail
from src.errors.errors import UserAlreadyExists, InvalidParams

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(blacklist_blueprint)
    return app.test_client()

def test_ping(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b'pong'

def test_reset_database(client, mocker):
    mock_reset = mocker.patch('src.commands.reset_database.ResetDatabase.execute')
    mock_reset.return_value = {"msg": "Todos los datos fueron eliminados"}

    headers = {
        'Authorization': 'Bearer valid_token'
    }
    response = client.post('/users/reset', headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {"msg": "Todos los datos fueron eliminados"}

def test_add_email_to_blacklist_success(client, mocker):
    mock_add_email = mocker.patch('src.commands.block_email.AddEmailToBlackList.execute')
    mock_add_email.return_value = {"message": "Successfully added email to blacklist"}

    headers = {
        'Authorization': 'Bearer valid_token'
    }
    data = {
        'email': 'test@example.com',
        'app_uuid': '550e8400-e29b-41d4-a716-446655440000',
        'blocked_reason': 'Testing reason'
    }
    response = client.post('/blacklist', json=data, headers=headers)

    assert response.status_code == 201
    assert response.get_json() == {"message": "Successfully added email to blacklist"}

def test_add_email_to_blacklist_user_already_exists(client, mocker):
    mock_add_email = mocker.patch('src.commands.block_email.AddEmailToBlackList.execute')
    mock_add_email.side_effect = UserAlreadyExists()

    headers = {
        'Authorization': 'Bearer valid_token'
    }
    data = {
        'email': 'existing@example.com',
        'app_uuid': '550e8400-e29b-41d4-a716-446655440000',
        'blocked_reason': 'Already exists test'
    }
    response = client.post('/blacklist', json=data, headers=headers)

    assert response.status_code == 412
    assert response.get_json() == {"error": "User already exists"}

def test_add_email_to_blacklist_invalid_params(client, mocker):
    mock_add_email = mocker.patch('src.commands.block_email.AddEmailToBlackList.execute')
    mock_add_email.side_effect = InvalidParams("Invalid parameters")

    headers = {
        'Authorization': 'Bearer valid_token'
    }
    data = {
        'email': '',
        'app_uuid': 'invalid-uuid',
        'blocked_reason': ''
    }
    response = client.post('/blacklist', json=data, headers=headers)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid parameters"}

def test_get_blocked_info_success(client, mocker):
    mock_get_blocked_info = mocker.patch('src.commands.get_blocked_info.IsBlockedEmail.execute')
    mock_get_blocked_info.return_value = {
        "blacklisted_email": True,
        "blocked_reason": "Testing reason"
    }

    headers = {
        'Authorization': 'Bearer valid_token'
    }
    response = client.get('/blacklist/test@example.com', headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {
        "blacklisted_email": True,
        "blocked_reason": "Testing reason"
    }

def test_get_blocked_info_not_in_blacklist(client, mocker):
    mock_get_blocked_info = mocker.patch('src.commands.get_blocked_info.IsBlockedEmail.execute')
    mock_get_blocked_info.return_value = {"blacklisted_email": False}

    headers = {
        'Authorization': 'Bearer valid_token'
    }
    response = client.get('/blacklist/not_in_list@example.com', headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {"blacklisted_email": False}

def test_get_blocked_info_missing_token(client):
    response = client.get('/blacklist/test@example.com')
    assert response.status_code == 403
