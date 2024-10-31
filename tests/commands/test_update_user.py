import pytest
from unittest.mock import MagicMock
from src.commands.update_user import UpdateUser
from src.errors.errors import InvalidParams, UserNotFound
from src.models.model import User
from src.models.schemas import UpdateUserSchema
from src.database import db_session

def test_update_user_success(mocker):
    # Mock the User object and the database session
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.status = 'active'
    mock_user.dni = '12345678A'
    mock_user.fullName = 'Test User'
    mock_user.phoneNumber = '123456789'
    
    # Mock the schema validation to return no errors
    mock_schema = mocker.patch('src.commands.update_user.UpdateUserSchema')
    mock_schema.return_value.validate.return_value = {}
    
    # Mock the db_session to return the mocked user
    mock_db_session = mocker.patch('src.commands.update_user.db_session')
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Create the UpdateUser instance
    command = UpdateUser(user_id=1, status='inactive', dni='87654321B', fullName='Updated User', phoneNumber='987654321')
    result = command.execute()

    # Check the result
    assert result['msg'] == 'el usuario ha sido actualizado'
    assert mock_user.status == 'inactive'
    assert mock_user.dni == '87654321B'
    assert mock_user.fullName == 'Updated User'
    assert mock_user.phoneNumber == '987654321'
    mock_db_session.commit.assert_called_once()

def test_update_user_not_found(mocker):
    # Mock the db_session to return None
    mock_db_session = mocker.patch('src.commands.update_user.db_session')
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    command = UpdateUser(user_id=999)  # Non-existing user ID
    
    with pytest.raises(UserNotFound):
        command.execute()

def test_update_user_invalid_params(mocker):
    # Mock the User object
    mock_user = MagicMock()
    mock_user.id = 1

    # Mock the schema validation to return errors
    mock_schema = mocker.patch('src.commands.update_user.UpdateUserSchema')
    mock_schema.return_value.validate.return_value = {'status': 'Invalid status'}

    # Mock the db_session to return the mocked user
    mock_db_session = mocker.patch('src.commands.update_user.db_session')
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    command = UpdateUser(user_id=1, status='invalid_status')  # Invalid status

    with pytest.raises(InvalidParams):
        command.execute()
