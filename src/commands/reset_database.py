# /commands/reset_database.py
from src.commands.base_command import BaseCommand
from src.database import db_session
from src.models.model import Blacklist


class ResetDatabase(BaseCommand):
    def execute(self):
        db_session.query(Blacklist).delete()
        db_session.commit()
        return {"msg": "Todos los datos fueron eliminados"}