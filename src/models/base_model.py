# user/src/models/base_model.py
from datetime import datetime
from sqlalchemy import Column, DateTime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Model:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
