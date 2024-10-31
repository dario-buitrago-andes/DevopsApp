from src.commands.base_command import BaseCommand
from src.models.model import Blacklist
from src.errors.errors import InvalidToken
from src.database import db_session


class IsBlockedEmail(BaseCommand):
    def __init__(self, email):
        self.email = email

    def execute(self):
        email = self.email
        if not email:
            raise InvalidToken()

        blocked_app = db_session.query(Blacklist).filter(Blacklist.email == email).first()
        if not blocked_app:
            return {"blocked_email": False}

        return {
            "blacklisted_email": True,
            "blocked_reason": blocked_app.blocked_reason
        }
