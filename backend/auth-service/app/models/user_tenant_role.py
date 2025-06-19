import uuid
from sqlalchemy import Column, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserTenantRole(Base):
    __tablename__ = "user_tenant_roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False, index=True)
    assigned_at = Column(DateTime, default=func.now(), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)  # User who assigned this role
    
    # Relationships
    user = relationship("User", back_populates="user_tenant_roles", foreign_keys=[user_id])
    tenant = relationship("Tenant", back_populates="user_tenant_roles")
    role = relationship("Role", back_populates="user_tenant_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
    
    # Ensure a user can only have one role per tenant (can be modified if needed)
    __table_args__ = (
        UniqueConstraint('user_id', 'tenant_id', name='unique_user_tenant'),
    )
    
    def __repr__(self):
        return f"<UserTenantRole user:{self.user_id} tenant:{self.tenant_id} role:{self.role_id}>"
