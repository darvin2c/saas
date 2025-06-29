import pytest
import uuid
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
from faker import Faker
from app.services.auth_service import AuthService
from app.models import User, Tenant, UserTenant
from app.schemas.auth import UserRegister, UserLogin, TokenData
from app.utils.auth import get_password_hash

# Inicializar Faker
fake = Faker()


@pytest.fixture
def test_tenant(db_session):
    tenant = Tenant(
        id=uuid.uuid4(),
        name=fake.company(),
        domain=f"test-{uuid.uuid4().hex[:8]}.com",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def inactive_tenant(db_session):
    tenant = Tenant(
        id=uuid.uuid4(),
        name=fake.company(),
        domain=f"inactive-{uuid.uuid4().hex[:8]}.com",
        is_active=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant





@pytest.fixture
def test_user(db_session):
    user = User(
        id=uuid.uuid4(),
        email=fake.email(),
        hashed_password=get_password_hash("password123"),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=True,
        is_verified=True,

        reset_password_token=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_login=None
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# Esta fixture ya no es necesaria ya que todos los usuarios están verificados por defecto
# Se mantiene para compatibilidad con pruebas existentes
@pytest.fixture
def unverified_user(db_session):
    user = User(
        id=uuid.uuid4(),
        email=fake.email(),
        hashed_password=get_password_hash("password123"),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=True,
        is_verified=True,
        reset_password_token=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_login=None
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_tenant(db_session, test_user, test_tenant):
    user_tenant = UserTenant(
        id=uuid.uuid4(),
        user_id=test_user.id,
        tenant_id=test_tenant.id,
        assigned_at=datetime.utcnow()
    )
    db_session.add(user_tenant)
    db_session.commit()
    db_session.refresh(user_tenant)
    return user_tenant


class TestAuthService:
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, db_session, test_tenant):
        # Arrange
        user_data = UserRegister(
            email=fake.email(),
            password=fake.password(length=12),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            tenant_domain=test_tenant.domain,
            tenant_name=test_tenant.name
        )
        
        # Act
        result = await AuthService.register_user(db_session, user_data)
        
        # Assert
        assert "user_id" in result
        assert result["message"] == "User registered successfully."
        assert result["requires_verification"] is False
        
        # Verify user was created in database
        user = db_session.query(User).filter(User.email == user_data.email).first()
        assert user is not None
        assert user.first_name == user_data.first_name
        assert user.last_name == user_data.last_name
        assert user.is_verified is True
        
        # Verify user-tenant relationship was created
        user_tenant = db_session.query(UserTenant).filter(
            UserTenant.user_id == user.id,
            UserTenant.tenant_id == test_tenant.id
        ).first()
        assert user_tenant is not None
    
    @pytest.mark.asyncio
    async def test_register_user_tenant_not_found(self, db_session):
        # Arrange
        tenant_domain = f"nonexistent-{uuid.uuid4().hex[:8]}.com"
        tenant_name = "New Test Tenant"
        user_data = UserRegister(
            email=fake.email(),
            password=fake.password(length=12),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            tenant_domain=tenant_domain,
            tenant_name=tenant_name
        )
        
        # Act
        result = await AuthService.register_user(db_session, user_data)
        
        # Assert
        assert "user_id" in result
        assert result["message"] == "User registered successfully."
        
        # Verify that a new tenant was created
        new_tenant = db_session.query(Tenant).filter(Tenant.domain == tenant_domain).first()
        assert new_tenant is not None
        assert new_tenant.name == tenant_name
    
    @pytest.mark.asyncio
    async def test_register_user_inactive_tenant(self, db_session, inactive_tenant):
        # Arrange
        user_data = UserRegister(
            email=fake.email(),
            password=fake.password(length=12),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            tenant_domain=inactive_tenant.domain,
            tenant_name=inactive_tenant.name
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Tenant is not active"):
            await AuthService.register_user(db_session, user_data)
    
    @pytest.mark.asyncio
    async def test_register_existing_user_new_tenant(self, db_session, test_user, test_tenant):
        # Create a new tenant
        new_tenant = Tenant(
            id=uuid.uuid4(),
            name=fake.company(),
            domain=f"second-{uuid.uuid4().hex[:8]}.com",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(new_tenant)
        db_session.commit()
        
        # Arrange - use existing user's email but with new tenant
        user_data = UserRegister(
            email=test_user.email,
            password=fake.password(length=12),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            tenant_domain=new_tenant.domain,
            tenant_name=new_tenant.name
        )
        
        # Act
        result = await AuthService.register_user(db_session, user_data)
        
        # Assert
        assert "user_id" in result
        assert result["user_id"] == test_user.id
        
        # Verify user-tenant relationship was created for the new tenant
        user_tenant = db_session.query(UserTenant).filter(
            UserTenant.user_id == test_user.id,
            UserTenant.tenant_id == new_tenant.id
        ).first()
        assert user_tenant is not None
    
    @pytest.mark.asyncio
    async def test_register_user_already_in_tenant(self, db_session, test_user, test_tenant, user_tenant):
        # Arrange - use existing user's email with same tenant
        user_data = UserRegister(
            email=test_user.email,
            password=fake.password(length=12),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            tenant_domain=test_tenant.domain,
            tenant_name=test_tenant.name
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="User already exists in this tenant"):
            await AuthService.register_user(db_session, user_data)
    
    def test_authenticate_user_success(self, db_session, test_user, test_tenant, user_tenant):
        # Arrange
        login_data = UserLogin(
            email=test_user.email,
            password="password123"
        )
        
        # Act
        result = AuthService.authenticate_user(db_session, login_data)
        
        # Assert
        assert result is not None
        # Verificar que el resultado es el usuario directamente, no un diccionario
        assert result.id == test_user.id
        assert result.email == test_user.email
        
        # Verify last login was updated
        updated_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert updated_user.last_login is not None
    
    def test_authenticate_user_wrong_password(self, db_session, test_user, test_tenant, user_tenant):
        # Arrange
        login_data = UserLogin(
            email=test_user.email,
            password="wrongpassword"
        )
        
        # Act
        result = AuthService.authenticate_user(db_session, login_data)
        
        # Assert
        assert result is None
    
    def test_authenticate_user_no_tenant_assigned(self, db_session):
        # Arrange - Create a user without any tenant assigned
        user = User(
            id=uuid.uuid4(),
            email=fake.email(),
            hashed_password=get_password_hash("password123"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_active=True,
            is_verified=True,
    
            reset_password_token=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login=None
        )
        db_session.add(user)
        db_session.commit()
        
        login_data = UserLogin(
            email=user.email,
            password="password123"
        )
        
        # Act
        result = AuthService.authenticate_user(db_session, login_data)
        
        # Assert
        # Ahora el test pasa si el usuario existe, incluso sin tenant asignado
        assert result is not None
        assert result.id == user.id
    
    def test_authenticate_user_multiple_tenants(self, db_session, test_user, test_tenant):
        # Arrange - Create a second active tenant and assign user to both
        second_tenant = Tenant(
            id=uuid.uuid4(),
            name=fake.company(),
            domain=f"second-{uuid.uuid4().hex[:8]}.com",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(second_tenant)
        db_session.commit()
        
        # Assign user to first tenant
        first_user_tenant = UserTenant(
            id=uuid.uuid4(),
            user_id=test_user.id,
            tenant_id=test_tenant.id,
            assigned_at=datetime.utcnow()
        )
        db_session.add(first_user_tenant)
        
        # Assign user to second tenant
        second_user_tenant = UserTenant(
            id=uuid.uuid4(),
            user_id=test_user.id,
            tenant_id=second_tenant.id,
            assigned_at=datetime.utcnow()
        )
        db_session.add(second_user_tenant)
        db_session.commit()
        
        login_data = UserLogin(
            email=test_user.email,
            password="password123"
        )
        
        # Act
        result = AuthService.authenticate_user(db_session, login_data)
        
        # Assert
        assert result is not None
        assert result.id == test_user.id
        
        # Verificar que el usuario tiene asignado ambos tenants
        user_tenants = db_session.query(UserTenant).filter(
            UserTenant.user_id == result.id
        ).all()
        assert len(user_tenants) == 2
    
    def test_create_user_tokens(self, db_session, test_user, test_tenant):
        # Arrange
        user_id = test_user.id
        
        # Act
        token = AuthService.create_user_tokens(user_id)
        
        # Assert
        assert token.access_token is not None
        assert token.refresh_token is not None
        assert len(token.access_token) > 0
        assert len(token.refresh_token) > 0
    
    @patch("app.services.auth_service.verify_token")
    def test_refresh_access_token_success(self, mock_verify_token, db_session, test_user, test_tenant, user_tenant):
        # Arrange
        mock_verify_token.return_value = {
            "sub": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        
        # Act
        token = AuthService.refresh_access_token(db_session, "valid_refresh_token")
        
        # Assert
        assert token is not None
        assert token.access_token is not None
        assert token.refresh_token is not None
    
    @patch("app.services.auth_service.verify_token")
    def test_refresh_access_token_invalid_token(self, mock_verify_token, db_session):
        # Arrange
        mock_verify_token.return_value = None
        
        # Act
        token = AuthService.refresh_access_token(db_session, "invalid_refresh_token")
        
        # Assert
        assert token is None
    
    @patch("app.services.auth_service.verify_token")
    def test_verify_access_token_success(self, mock_verify_token, db_session, test_user, test_tenant):
        # Arrange
        mock_verify_token.return_value = {
            "sub": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        # Act
        token_data = AuthService.verify_access_token(db_session, "valid_access_token")
        
        # Assert
        assert token_data is not None
        assert token_data.user_id == test_user.id
    
    @patch("app.services.auth_service.verify_token")
    def test_verify_access_token_invalid_token(self, mock_verify_token, db_session):
        # Arrange
        mock_verify_token.return_value = None
        
        # Act
        token_data = AuthService.verify_access_token(db_session, "invalid_access_token")
        
        # Assert
        assert token_data is None
    

    @pytest.mark.asyncio
    @patch("app.services.user_service.UserService.initiate_password_reset")
    @patch("app.utils.email.send_reset_password_email", new_callable=AsyncMock)
    async def test_request_password_reset_success(self, mock_send_email, mock_initiate_reset, db_session, test_user, test_tenant):
        # Arrange
        mock_initiate_reset.return_value = test_user
        
        # Act
        result = await AuthService.request_password_reset(db_session, test_user.email, test_tenant.domain)
        
        # Assert
        assert result is True
        mock_send_email.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("app.services.user_service.UserService.initiate_password_reset")
    async def test_request_password_reset_user_not_found(self, mock_initiate_reset, db_session, test_tenant):
        # Arrange
        mock_initiate_reset.return_value = None
        
        # Act
        result = await AuthService.request_password_reset(db_session, fake.email(), test_tenant.domain)
        
        # Assert
        assert result is False
    
    def test_reset_password_success(self, db_session):
        # Act
        with patch("app.services.user_service.UserService.reset_password", return_value=True):
            result = AuthService.reset_password(db_session, str(uuid.uuid4()), fake.password(length=12))
        
        # Assert
        assert result is True
    
    def test_reset_password_failure(self, db_session):
        # Act
        with patch("app.services.user_service.UserService.reset_password", return_value=False):
            result = AuthService.reset_password(db_session, "invalid_token", fake.password(length=12))
        
        # Assert
        assert result is False
