import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.main import app
from app.models import User, Tenant, UserTenant
from app.utils.auth import get_password_hash, create_access_token
from app.services.user_service import UserService
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
def test_user_with_tenant(db_session, test_user, test_tenant):
    """Fixture para crear una relación usuario-tenant."""
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


@pytest.fixture
def auth_headers(test_user):
    """Fixture para crear headers de autenticación."""
    access_token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}


class TestUsersAPI:
    """Pruebas para la API de usuarios."""

    def test_check_email_exists(self, db_session, test_user):
        """Prueba la verificación de email existente."""
        # Realizar la solicitud
        response = client.get(f"/users/exists?email={test_user.email}")
        
        # Verificar la respuesta
        assert response.status_code == 200
        assert response.json()["exists"] is True

    def test_check_email_not_exists(self, db_session):
        """Prueba la verificación de email no existente."""
        # Realizar la solicitud
        non_existent_email = f"non-existent-{uuid.uuid4().hex[:8]}@example.com"
        response = client.get(f"/users/exists?email={non_existent_email}")
        
        # Verificar la respuesta
        assert response.status_code == 200
        assert response.json()["exists"] is False

    def test_get_current_user_info_success(self, db_session, test_user, auth_headers):
        """Prueba obtener información del usuario actual con éxito."""
        # Realizar la solicitud
        response = client.get("/users/me", headers=auth_headers)
        
        # Verificar la respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name

    def test_get_current_user_info_unauthorized(self, db_session):
        """Prueba obtener información del usuario actual sin autenticación."""
        # Realizar la solicitud sin token
        response = client.get("/users/me")
        
        # Verificar la respuesta
        assert response.status_code == 403

    def test_update_current_user_success(self, db_session, test_user, auth_headers):
        """Prueba actualizar información del usuario actual con éxito."""
        # Datos para actualizar
        update_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name()
        }
        
        # Realizar la solicitud
        response = client.patch("/users/me", json=update_data, headers=auth_headers)
        
        # Verificar la respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        
        # Verificar que los cambios se guardaron en la base de datos
        db_session.refresh(test_user)
        assert test_user.first_name == update_data["first_name"]
        assert test_user.last_name == update_data["last_name"]

    def test_update_current_user_unauthorized(self, db_session):
        """Prueba actualizar información del usuario actual sin autenticación."""
        # Datos para actualizar
        update_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name()
        }
        
        # Realizar la solicitud sin token
        response = client.patch("/users/me", json=update_data)
        
        # Verificar la respuesta
        assert response.status_code == 403

    def test_get_users_success(self, db_session, test_user, test_tenant, test_user_with_tenant, auth_headers):
        """Prueba obtener lista de usuarios con éxito."""
        # Realizar la solicitud
        response = client.get(f"/users/?tenant_id={test_tenant.id}", headers=auth_headers)
        
        # Verificar la respuesta
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(user["id"] == str(test_user.id) for user in data)

    def test_get_users_unauthorized(self, db_session, test_tenant):
        """Prueba obtener lista de usuarios sin autenticación."""
        # Realizar la solicitud sin token
        response = client.get(f"/users/?tenant_id={test_tenant.id}")
        
        # Verificar la respuesta
        assert response.status_code == 403

    def test_get_user_by_id_success(self, db_session, test_user, test_tenant, test_user_with_tenant, auth_headers):
        """Prueba obtener usuario por ID con éxito."""
        # Realizar la solicitud
        response = client.get(f"/users/{test_user.id}?tenant_id={test_tenant.id}", headers=auth_headers)
        
        # Verificar la respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name

    def test_get_user_by_id_not_found(self, db_session, test_tenant, auth_headers):
        """Prueba obtener usuario por ID no existente."""
        # ID de usuario no existente
        non_existent_id = uuid.uuid4()
        
        # Realizar la solicitud
        response = client.get(f"/users/{non_existent_id}?tenant_id={test_tenant.id}", headers=auth_headers)
        
        # Verificar la respuesta - la API devuelve 403 porque primero verifica si el usuario pertenece al tenant
        assert response.status_code == 403
        assert "User does not belong to this tenant" in response.json().get("detail", "")

    def test_get_user_by_id_unauthorized(self, db_session, test_user, test_tenant):
        """Prueba obtener usuario por ID sin autenticación."""
        # Realizar la solicitud sin token
        response = client.get(f"/users/{test_user.id}?tenant_id={test_tenant.id}")
        
        # Verificar la respuesta
        assert response.status_code == 403

    def test_create_user_success(self, db_session, test_user, test_tenant, test_user_with_tenant, auth_headers):
        """Prueba crear usuario con éxito."""
        # Datos para el nuevo usuario
        user_data = {
            "email": fake.email(),
            "password": "TestPassword123!",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "is_active": True
        }
        
        # Realizar la solicitud
        response = client.post(f"/users/?tenant_id={test_tenant.id}", json=user_data, headers=auth_headers)
        
        # Verificar la respuesta - la API devuelve 200 en lugar de 201
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert "id" in data

    def test_create_user_unauthorized(self, db_session, test_tenant):
        """Prueba crear usuario sin autenticación."""
        # Datos para el nuevo usuario
        user_data = {
            "email": fake.email(),
            "password": "TestPassword123!",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "is_active": True
        }
        
        # Realizar la solicitud sin token
        response = client.post(f"/users/?tenant_id={test_tenant.id}", json=user_data)
        
        # Verificar la respuesta
        assert response.status_code == 403

    def test_update_user_success(self, db_session, test_user, test_tenant, test_user_with_tenant, auth_headers):
        """Prueba actualizar usuario por ID con éxito."""
        # Datos para actualizar
        update_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name()
        }
        
        # Realizar la solicitud
        response = client.patch(f"/users/{test_user.id}?tenant_id={test_tenant.id}", json=update_data, headers=auth_headers)
        
        # Verificar la respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        
        # Verificar que los cambios se guardaron en la base de datos
        db_session.refresh(test_user)
        assert test_user.first_name == update_data["first_name"]
        assert test_user.last_name == update_data["last_name"]

    def test_update_user_not_found(self, db_session, test_user, test_tenant, test_user_with_tenant, auth_headers):
        """Prueba actualizar usuario por ID no existente."""
        # ID de usuario no existente
        non_existent_id = uuid.uuid4()
        
        # Datos para actualizar
        update_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name()
        }
        
        # Realizar la solicitud
        response = client.patch(f"/users/{non_existent_id}?tenant_id={test_tenant.id}", json=update_data, headers=auth_headers)
        
        # Verificar la respuesta
        assert response.status_code == 404
        assert "User not found" in response.json().get("detail", "")

    def test_update_user_unauthorized(self, db_session, test_user, test_tenant):
        """Prueba actualizar usuario por ID sin autenticación."""
        # Datos para actualizar
        update_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name()
        }
        
        # Realizar la solicitud sin token
        response = client.patch(f"/users/{test_user.id}?tenant_id={test_tenant.id}", json=update_data)
        
        # Verificar la respuesta
        assert response.status_code == 403

    def test_delete_user_success(self, db_session, test_user, test_tenant, test_user_with_tenant, auth_headers):
        """Prueba eliminar usuario por ID con éxito."""
        # Crear un usuario adicional para eliminar
        password_hash = get_password_hash("testpassword123")
        user_to_delete = User(
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
        db_session.add(user_to_delete)
        db_session.commit()
        
        # Asociar el usuario al tenant
        user_tenant = UserTenant(
            id=uuid.uuid4(),
            user_id=user_to_delete.id,
            tenant_id=test_tenant.id,
            assigned_at=datetime.utcnow()
        )
        db_session.add(user_tenant)
        db_session.commit()
        
        # Realizar la solicitud
        response = client.delete(f"/users/{user_to_delete.id}?tenant_id={test_tenant.id}", headers=auth_headers)
        
        # Verificar la respuesta
        assert response.status_code == 200
        assert response.json()["message"] == "User removed from tenant successfully"
        
        # Verificar que la relación usuario-tenant se eliminó
        user_tenant_relation = db_session.query(UserTenant).filter_by(
            user_id=user_to_delete.id, 
            tenant_id=test_tenant.id
        ).first()
        assert user_tenant_relation is None

    def test_delete_user_not_found(self, db_session, test_tenant, auth_headers):
        """Prueba eliminar usuario por ID no existente."""
        # ID de usuario no existente
        non_existent_id = uuid.uuid4()
        
        # Realizar la solicitud
        response = client.delete(f"/users/{non_existent_id}?tenant_id={test_tenant.id}", headers=auth_headers)
        
        # Verificar la respuesta - la API devuelve 403 porque primero verifica si el usuario pertenece al tenant
        assert response.status_code == 403
        assert "User does not belong to this tenant" in response.json().get("detail", "")

    def test_delete_user_unauthorized(self, db_session, test_user, test_tenant):
        """Prueba eliminar usuario por ID sin autenticación."""
        # Realizar la solicitud sin token
        response = client.delete(f"/users/{test_user.id}?tenant_id={test_tenant.id}")
        
        # Verificar la respuesta
        assert response.status_code == 403
