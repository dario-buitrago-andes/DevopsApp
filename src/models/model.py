from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from src.models.base_model import Model

Base = declarative_base()


class Blacklist(Model, Base):
    __tablename__ = 'blacklist'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    app_uuid = Column(String, nullable=False)
    blocked_reason = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, email, app_uuid, blocked_reason, ip_address, created_at):
        Model.__init__(self)
        self.email = email
        self.app_uuid = app_uuid
        self.blocked_reason = blocked_reason
        self.ip_address = ip_address
        self.created_at = created_at
