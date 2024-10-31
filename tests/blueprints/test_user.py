import pytest
import uuid
from unittest.mock import MagicMock
from flask import Flask
from flask.testing import FlaskClient
from src.blueprints.user import user_blueprint
from src.commands.create_user import CreateUser
from src.commands.update_user import UpdateUser
from src.errors.errors import UserPasswordError, UserAlreadyExists, InvalidParams, UserNotFound, InvalidToken, TokenExpired, MissingTokenError

@pytest.fixture
def client() -> FlaskClient:
    app = Flask(__name__)
    app.register_blueprint(user_blueprint)
    return app.test_client()


def test_create_user_user_already_exists(client: FlaskClient, mocker):
    # Mock the schema validation to return no errors
    mock_schema = mocker.patch('src.commands.create_user.CreateUserInputSchema')
    mock_schema.return_value.validate.return_value = {}

    # Mock db_session to simulate existing user
    mock_db_session = mocker.patch('src.commands.create_user.db_session')
    mock_db_session.query.return_value.filter.return_value.first.return_value = MagicMock()

    # Simular una solicitud POST para crear un usuario       
    response = client.post('/users', json={
        'username': 'test_user',
        'password': 'password',
        'email': 'test@example.com',
        'dni': '12345678A',
        'fullName': 'Test User',
        'phoneNumber': '123456789'
    })

    # Verificar el código de estado de la respuesta
    assert response.status_code == 412
    assert response.data == b''


def test_create_user_internal_server_error(client: FlaskClient, mocker):
    # Mock the schema validation to return no errors
    mock_schema = mocker.patch('src.commands.create_user.CreateUserInputSchema')
    mock_schema.return_value.validate.return_value = {}

    # Mock db_session to raise an unexpected exception
    mock_db_session = mocker.patch('src.commands.create_user.db_session')
    mock_db_session.query.side_effect = Exception('Unexpected error')

    # Simular una solicitud POST para crear un usuario       
    response = client.post('/users', json={
        'username': 'test_user',
        'password': 'password',
        'email': 'test@example.com',
        'dni': '12345678A',
        'fullName': 'Test User',
        'phoneNumber': '123456789'
    })

    # Verificar el código de estado de la respuesta
    assert response.status_code == 400
    assert b'Unexpected error' in response.data


def test_ping(client: FlaskClient):
    # Simulate a GET request to the /users/ping endpoint
    response = client.get('/users/ping')
    
    # Verify the status code of the response
    assert response.status_code == 200
    
    # Verify the content of the response
    assert response.data == b'pong'


def test_get_user_info_missing_token(client: FlaskClient):
    # Simulate a GET request to the /users/me endpoint without an Authorization header
    response = client.get('/users/me')

    # Verify the status code of the response
    assert response.status_code == 403, f"Expected 403 FORBIDDEN, got {response.status_code} instead."

    # Verify the content of the response
    expected_message = b'Token is missing. Please log in again.'
    assert response.data == expected_message, f"Expected message '{expected_message.decode()}', got '{response.data.decode()}' instead."

def test_generate_token_success(client: FlaskClient, mocker):
    # Mock the command to return a successful result
    mock_generate_token = mocker.patch('src.commands.generate_token.GenerateToken.execute')
    mock_generate_token.return_value = {
        'token': 'valid_token'
    }

    # Simulate a POST request to the /users/auth endpoint
    response = client.post('/users/auth', json={
        'username': 'test_user',
        'password': 'password'
    })

    # Verify the status code of the response
    assert response.status_code == 200

    # Verify the content of the response
    json_data = response.get_json()
    assert 'token' in json_data
    assert json_data['token'] == 'valid_token'


def test_generate_token_invalid_params(client: FlaskClient, mocker):
    # Mock the command to raise an InvalidParams error
    mock_generate_token = mocker.patch('src.commands.generate_token.GenerateToken.execute')
    mock_generate_token.side_effect = InvalidParams('Invalid parameters')

    # Simulate a POST request to the /users/auth endpoint
    response = client.post('/users/auth', json={
        'username': '',
        'password': 'password'
    })

    # Verify the status code of the response
    assert response.status_code == 400

    # Verify the content of the response
    assert b'Invalid parameters' in response.data


def test_generate_token_user_not_found(client: FlaskClient, mocker):
    # Mock the command to raise a UserNotFound error
    mock_generate_token = mocker.patch('src.commands.generate_token.GenerateToken.execute')
    mock_generate_token.side_effect = UserNotFound('User not found')

    # Simulate a POST request to the /users/auth endpoint
    response = client.post('/users/auth', json={
        'username': 'nonexistent_user',
        'password': 'password'
    })

    # Verify the status code of the response
    assert response.status_code == 404

    # Verify the content of the response
    assert b'User not found' in response.data


def test_update_user_success(client: FlaskClient, mocker):
    # Mock UpdateUser command to return a successful result
    mock_update_user = mocker.patch('src.commands.update_user.UpdateUser.execute')
    mock_update_user.return_value = {'status': 'updated'}

    user_id = str(uuid.uuid4())
    response = client.patch(f'/users/{user_id}', json={
        'status': 'active',
        'dni': '12345678A',
        'fullName': 'Updated User',
        'phoneNumber': '123456789'
    })

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'updated'


def test_update_user_invalid_params(client: FlaskClient, mocker):
    # Mock UpdateUser command to raise an InvalidParams error
    mock_update_user = mocker.patch('src.commands.update_user.UpdateUser.execute')
    mock_update_user.side_effect = InvalidParams()

    user_id = str(uuid.uuid4())
    response = client.patch(f'/users/{user_id}', json={
        'status': '',
        'dni': '12345678A',
        'fullName': '',
        'phoneNumber': ''
    })

    assert response.status_code == 400


def test_update_user_not_found(client: FlaskClient, mocker):
    # Mock UpdateUser command to raise a UserNotFound error
    mock_update_user = mocker.patch('src.commands.update_user.UpdateUser.execute')
    mock_update_user.side_effect = UserNotFound()

    user_id = str(uuid.uuid4())
    response = client.patch(f'/users/{user_id}', json={
        'status': 'active',
        'dni': '12345678A',
        'fullName': 'Updated User',
        'phoneNumber': '123456789'
    })

    assert response.status_code == 404


def test_update_user_invalid_uuid(client: FlaskClient):
    # Simulate a PATCH request with an invalid UUID
    response = client.patch('/users/invalid-uuid', json={
        'status': 'active',
        'dni': '12345678A',
        'fullName': 'Updated User',
        'phoneNumber': '123456789'
    })

    assert response.status_code == 400

def test_get_user_info_invalid_token(client: FlaskClient, mocker):
    # Mock GetUserInfo command to raise an InvalidToken error
    mock_get_user_info = mocker.patch('src.commands.get_user_info.GetUserInfo.execute')
    mock_get_user_info.side_effect = InvalidToken()

    response = client.get('/users/me', headers={'Authorization': 'Bearer invalid_token'})

    assert response.status_code == 401

