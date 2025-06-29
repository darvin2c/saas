import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.main import app
from app.models import User, Tenant, Role, UserTenantRole
from app.utils.auth import get_password_hash, create_access_token
from app.services.auth_service import AuthService
import uuid
from datetime import datetime, timedelta
from faker import Faker

# Inicializar Faker
fake = Faker()

# Cliente de prueba
client = TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Fixture para crear un usuario de prueba."""
    password_hash = get_password_hash("testpassword123")
    user = User(
        id=uuid.uuid4(),
        email=fake.email(),
        hashed_password=password_hash,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_tenant(db_session):
    """Fixture para crear un tenant de prueba."""
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
def test_role(db_session):
    """Fixture para crear un rol de prueba."""
    role = Role(
        id=uuid.uuid4(),
        name="User",
        description="Regular user role",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def test_user_with_tenant_role(db_session, test_user, test_tenant, test_role):
    """Fixture para crear una relación usuario-tenant-rol."""
    user_tenant_role = UserTenantRole(
        id=uuid.uuid4(),
        user_id=test_user.id,
        tenant_id=test_tenant.id,
        role_id=test_role.id,
        assigned_at=datetime.utcnow()
    )
    db_session.add(user_tenant_role)
    db_session.commit()
    db_session.refresh(user_tenant_role)
    return user_tenant_role


@pytest.fixture
def auth_headers(test_user):
    """Fixture para crear headers de autenticación."""
    access_token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}


class TestAuthAPI:
    """Pruebas para la API de autenticación."""

    def test_register_user_success(self, db_session, monkeypatch):
        """Prueba el registro exitoso de un usuario."""
        # Mock para el servicio de autenticación
        async def mock_register(*args, **kwargs):
            return {
                "user_id": str(uuid.uuid4()),
                "message": "User registered successfully.",
                "requires_verification": False
            }
        
        monkeypatch.setattr(AuthService, "register_user", mock_register)
        
        # Datos de prueba
        user_data = {
            "email": fake.email(),
            "password": "TestPassword123!",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "tenant_domain": f"test-{uuid.uuid4().hex[:8]}.com",
            "tenant_name": fake.company()
        }
        
        # Realizar la solicitud
        response = client.post("/register", json=user_data)
        
        # Verificar la respuesta
        assert response.status_code == 200
        assert "user_id" in response.json()
        assert response.json()["message"] == "User registered successfully."
        assert response.json()["requires_verification"] is False

    def test_login_success(self, db_session, test_user, monkeypatch):
        """Prueba el inicio de sesión exitoso."""
        # Mock para el servicio de autenticación
        def mock_authenticate(*args, **kwargs):
            return test_user
        
        def mock_create_tokens(*args, **kwargs):
            return {
                "access_token": "mock_access_token",
                "refresh_token": "mock_refresh_token",
                "token_type": "bearer"
            }
        
        monkeypatch.setattr(AuthService, "authenticate_user", mock_authenticate)
        monkeypatch.setattr(AuthService, "create_user_tokens", mock_create_tokens)
        
        # Datos de prueba
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        # Realizar la solicitud
        response = client.post("/login", json=login_data)
        
        # Verificar la respuesta
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_invalid_credentials(self, db_session, monkeypatch):
        """Prueba el inicio de sesión con credenciales inválidas."""
        # Mock para el servicio de autenticación
        def mock_authenticate(*args, **kwargs):
            return None
        
        monkeypatch.setattr(AuthService, "authenticate_user", mock_authenticate)
        
        # Datos de prueba
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        # Realizar la solicitud
        response = client.post("/login", json=login_data)
        
        # Verificar la respuesta
        assert response.status_code == 401
        assert "detail" in response.json()
        assert response.json()["detail"] == "Incorrect email or password"

    def test_refresh_token_success(self, db_session, test_user, monkeypatch):
        """Prueba la renovación exitosa del token."""
        # Mock para el servicio de autenticación
        def mock_refresh(*args, **kwargs):
            return {
                "access_token": "new_mock_access_token",
                "refresh_token": "new_mock_refresh_token",
                "token_type": "bearer"
            }
        
        monkeypatch.setattr(AuthService, "refresh_access_token", mock_refresh)
        
        # Datos de prueba
        refresh_data = {
            "refresh_token": "valid_refresh_token"
        }
        
        # Realizar la solicitud
        response = client.post("/refresh", json=refresh_data)
        
        # Verificar la respuesta
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_request_password_reset_success(self, db_session, test_user, monkeypatch):
        """Prueba la solicitud exitosa de restablecimiento de contraseña."""
        # Mock para el servicio de autenticación
        async def mock_request_reset(*args, **kwargs):
            return {"message": "Password reset email sent"}
        
        monkeypatch.setattr(AuthService, "request_password_reset", mock_request_reset)
        
        # Datos de prueba
        reset_data = {
            "email": test_user.email,
            "tenant_domain": "example.com"
        }
        
        # Realizar la solicitud
        response = client.post("/request-password-reset", json=reset_data)
        
        # Verificar la respuesta
        assert response.status_code == 200
        assert response.json()["message"] == "If the email exists, a password reset link has been sent"

    def test_reset_password_success(self, db_session, test_user, monkeypatch):
        """Prueba el restablecimiento exitoso de contraseña."""
        # Mock para el servicio de autenticación
        def mock_reset_password(*args, **kwargs):
            return {"message": "Password reset successfully"}
        
        monkeypatch.setattr(AuthService, "reset_password", mock_reset_password)
        
        # Datos de prueba
        reset_data = {
            "token": "valid_reset_token",
            "new_password": "NewPassword123!"
        }
        
        # Realizar la solicitud
        response = client.post("/reset-password", json=reset_data)
        
        # Verificar la respuesta
        assert response.status_code == 200
        assert response.json()["message"] == "Password reset successfully"
