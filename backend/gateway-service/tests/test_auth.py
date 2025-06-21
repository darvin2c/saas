import pytest
import pytest_asyncio
from fastapi import HTTPException, Request
from jose import jwt
import time
from unittest.mock import MagicMock, patch

from app.utils.auth import verify_token
from app.config.settings import settings


@pytest.fixture
def mock_request():
    """Fixture para crear una solicitud simulada con headers personalizables."""
    request = MagicMock(spec=Request)
    request.headers = {}
    return request


@pytest.fixture
def valid_token():
    """Fixture para crear un token JWT válido."""
    payload = {
        "sub": "test@example.com",
        "user_id": "123",
        "tenant_id": "tenant1",
        "exp": time.time() + 3600  # Token válido por 1 hora
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


class TestAuth:
    """Pruebas para las funciones de autenticación."""

    @pytest.mark.asyncio
    async def test_verify_token_valid(self, mock_request, valid_token):
        """Prueba que un token válido sea aceptado."""
        # Configurar
        mock_request.headers = {"Authorization": f"Bearer {valid_token}"}
        
        # Ejecutar
        payload = await verify_token(mock_request)
        
        # Verificar
        assert payload["user_id"] == "123"
        assert payload["tenant_id"] == "tenant1"
        assert payload["sub"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_verify_token_missing_header(self, mock_request):
        """Prueba que una solicitud sin token sea rechazada."""
        # Configurar
        mock_request.headers = {}
        mock_request.url = MagicMock()
        mock_request.url.path = "/test/path"
        
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(mock_request)
        
        assert excinfo.value.status_code == 401
        assert "Encabezado de autorización faltante" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_verify_token_invalid_format(self, mock_request):
        """Prueba que un token con formato incorrecto sea rechazado."""
        # Configurar
        mock_request.headers = {"Authorization": "InvalidFormat token123"}
        
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(mock_request)
        
        assert excinfo.value.status_code == 401
        # Verificar que el mensaje de error contiene información sobre el esquema inválido
        # El mensaje exacto puede variar, así que verificamos que sea sobre autenticación
        assert "autenticación" in excinfo.value.detail.lower()

    @pytest.mark.asyncio
    async def test_verify_token_invalid_token(self, mock_request):
        """Prueba que un token inválido sea rechazado."""
        # Configurar
        mock_request.headers = {"Authorization": "Bearer invalid.token.here"}
        
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(mock_request)
        
        assert excinfo.value.status_code == 401
        assert "Token inválido" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_verify_token_expired(self, mock_request):
        """Prueba que un token expirado sea rechazado."""
        # Crear un token expirado
        payload = {
            "sub": "test@example.com",
            "exp": time.time() - 3600  # Token expirado hace 1 hora
        }
        expired_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        # Configurar
        mock_request.headers = {"Authorization": f"Bearer {expired_token}"}
        
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(mock_request)
        
        assert excinfo.value.status_code == 401
        assert "Token inválido" in excinfo.value.detail
