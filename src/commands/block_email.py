from datetime import datetime
from src.commands.base_command import BaseCommand
from src.models.model import Blacklist
from src.errors.errors import InvalidParams, UserAlreadyExists, ApiError
from src.database import db_session
from src.models.schemas import ToBlacklistSchema


class AddEmailToBlackList(BaseCommand):
    def __init__(self, email, app_uuid, blocked_reason, ip_address):
        self.email = email
        self.app_uuid = app_uuid
        self.blocked_reason = blocked_reason
        self.ip_address = ip_address

    def execute(self):
        input_schema = ToBlacklistSchema()

        input_data = {
            "email": self.email,
            "app_uuid": self.app_uuid,
            "blocked_reason": self.blocked_reason
        }

        errors = input_schema.validate(input_data)
        if errors:
            raise InvalidParams(errors)

        blocked_email = db_session.query(Blacklist).filter((Blacklist.email == self.email)
        ).first()
        if blocked_email:
            raise UserAlreadyExists()

        new_blocked = Blacklist(
            email=self.email,
            app_uuid=self.app_uuid,
            blocked_reason=self.blocked_reason,
            ip_address=self.ip_address,
            created_at=datetime.now()
        )

        db_session.add(new_blocked)
        db_session.commit()

        return{"message": "Successfully added email to blacklist"}
