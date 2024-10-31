import pytest
from unittest.mock import MagicMock
from src.commands.reset_database import ResetDatabase
from src.models.model import User
from src.database import db_session

def test_reset_database_success(mocker):
    # Mock the db_session and User model
    mock_db_session = mocker.patch('src.commands.reset_database.db_session')
    mock_db_session.query.return_value.delete.return_value = None  # Mock the delete method
    mock_db_session.commit.return_value = None  # Mock the commit method

    # Create the ResetDatabase instance
    command = ResetDatabase()
    result = command.execute()

    # Check the result
    assert result['msg'] == 'Todos los datos fueron eliminados'
    mock_db_session.query.return_value.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()

@pytest.mark.parametrize("delete_side_effect", [Exception("Delete failed"), None])
def test_reset_database_failure(mocker, delete_side_effect):
    # Mock the db_session and User model
    mock_db_session = mocker.patch('src.commands.reset_database.db_session')
    mock_db_session.query.return_value.delete.side_effect = delete_side_effect  # Simulate delete failure
    mock_db_session.commit.return_value = None  # Mock the commit method

    command = ResetDatabase()
    
    if delete_side_effect:
        with pytest.raises(Exception, match="Delete failed"):
            command.execute()
    else:
        # Simulate successful delete but failure in commit
        mock_db_session.commit.side_effect = Exception("Commit failed")
        with pytest.raises(Exception, match="Commit failed"):
            command.execute()
