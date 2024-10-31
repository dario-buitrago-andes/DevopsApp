import pytest
from unittest.mock import MagicMock
from src.commands.get_user_info import GetUserInfo
from src.errors.errors import InvalidToken, UserNotFound
from src.models.model import User
from src.database import db_session
import uuid

def test_execute_success(mocker):
    # Mock the User object and the database session
    mock_user = MagicMock()
    mock_user.username = 'test_user'
    mock_user.email = 'test@example.com'
    mock_user.fullName = 'Test User'
    mock_user.dni = '12345678A'
    mock_user.phoneNumber = '123456789'
    mock_user.status.value = 'active'
    
    # Mock decode_token to return a specific user_id
    mocker.patch('src.commands.get_user_info.decode_token', return_value='550e8400-e29b-41d4-a716-446655440000')

    # Mock the db_session to return the mocked user
    mock_db_session = mocker.patch('src.commands.get_user_info.db_session')
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Create the GetUserInfo instance
    token = 'valid_token'
    command = GetUserInfo(token=token)
    result = command.execute()

    # Check the result
    assert result['id'] == '550e8400-e29b-41d4-a716-446655440000'
    assert result['username'] == 'test_user'
    assert result['email'] == 'test@example.com'
    assert result['fullName'] == 'Test User'
    assert result['dni'] == '12345678A'
    assert result['phoneNumber'] == '123456789'
    assert result['status'] == 'active'

def test_execute_invalid_token(mocker):
    # Mock decode_token to return None (indicating invalid token)
    mocker.patch('src.commands.get_user_info.decode_token', return_value=None)
    
    command = GetUserInfo(token='invalid_token')
    
    with pytest.raises(InvalidToken):
        command.execute()

def test_execute_user_not_found(mocker):
    # Mock decode_token to return a specific user_id
    mocker.patch('src.commands.get_user_info.decode_token', return_value='550e8400-e29b-41d4-a716-446655440000')

    # Mock the db_session to return None for the user query
    mock_db_session = mocker.patch('src.commands.get_user_info.db_session')
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    command = GetUserInfo(token='valid_token')
    
    with pytest.raises(UserNotFound):
        command.execute()
