import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False)  # e.g., 'users', 'appointments', 'reports'
    action = Column(String(20), nullable=False)   # e.g., 'create', 'read', 'update', 'delete'
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Permission {self.name}: {self.action} on {self.resource}>"
