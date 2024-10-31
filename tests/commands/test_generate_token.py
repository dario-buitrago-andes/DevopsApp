import pytest
from unittest.mock import MagicMock
from src.commands.generate_token import GenerateToken, decode_token
from src.errors.errors import InvalidParams, UserNotFound, UserPasswordError, TokenExpired, InvalidToken
from jose import jwt
from datetime import datetime, timezone, timedelta

from src.models.model import UserStatus

SECRET_KEY = "your_secret_key"

def test_execute_success(mocker):
    # Mock the User object and the database session
    mock_user = MagicMock()
    mock_user.username = 'test_user'
    mock_user.password = 'hashed_password'
    mock_user.salt = 'salt'
    mock_user.id = 1
    mock_user.status = UserStatus.VERIFICADO

    mock_db_session = mocker.patch('src.commands.generate_token.db_session')
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Mock the hash_password method
    mocker.patch.object(GenerateToken, 'hash_password', return_value='hashed_password')

    # Create the GenerateToken instance
    command = GenerateToken(username='test_user', password='password')
    result = command.execute()

    # Check the result
    assert result['id'] == 1
    assert 'token' in result
    assert 'expireAt' in result

def test_execute_user_not_found(mocker):
    # Mock the database session to return None
    mock_db_session = mocker.patch('src.commands.generate_token.db_session')
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    command = GenerateToken(username='invalid_user', password='password')

    with pytest.raises(UserNotFound):
        command.execute()

def test_execute_password_error(mocker):
    # Mock the User object
    mock_user = MagicMock()
    mock_user.username = 'test_user'
    mock_user.password = 'wrong_password'
    mock_user.salt = 'salt'
    mock_user.id = 1

    mock_db_session = mocker.patch('src.commands.generate_token.db_session')
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Mock the hash_password method
    mocker.patch.object(GenerateToken, 'hash_password', return_value='hashed_password')

    command = GenerateToken(username='test_user', password='password')

    with pytest.raises(UserPasswordError):
        command.execute()

def test_decode_token_success(mocker):
    # Mock jwt.decode to return a payload
    mocker.patch('jose.jwt.decode', return_value={"user_id": "1"})
    
    token = jwt.encode({"user_id": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
    user_id = decode_token(token)
    
    assert user_id == "1"

def test_decode_token_expired(mocker):
    # Mock jwt.decode to raise an ExpiredSignatureError
    mocker.patch('jose.jwt.decode', side_effect=jwt.ExpiredSignatureError)
    
    token = jwt.encode({"user_id": "1", "exp": datetime.now(timezone.utc) - timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
    
    with pytest.raises(TokenExpired):
        decode_token(token)

def test_decode_token_invalid(mocker):
    # Mock jwt.decode to raise a JWTError
    mocker.patch('jose.jwt.decode', side_effect=jwt.JWTError)
    
    token = jwt.encode({"user_id": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
    
    with pytest.raises(InvalidToken):
        decode_token(token)
