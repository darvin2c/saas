import pytest
from fastapi import Request, HTTPException
from unittest.mock import MagicMock, patch, AsyncMock

from app.api.router import is_public_path, service_proxy
from app.config.settings import settings


class TestIsPublicPath:
    """Pruebas para la función is_public_path."""

    def test_exact_match(self):
        """Prueba que una ruta exacta en public_paths se identifique como pública."""
        public_paths = ["login", "register", "health"]
        assert is_public_path("login", public_paths) is True
        assert is_public_path("register", public_paths) is True
        assert is_public_path("health", public_paths) is True

    def test_subpath_match(self):
        """Prueba que una subruta de una ruta pública se identifique como pública."""
        public_paths = ["login", "health"]
        assert is_public_path("login/refresh", public_paths) is True
        assert is_public_path("health/status", public_paths) is True

    def test_non_public_path(self):
        """Prueba que una ruta no pública se identifique como privada."""
        public_paths = ["login", "register", "health"]
        assert is_public_path("users", public_paths) is False
        assert is_public_path("admin", public_paths) is False


@pytest.fixture
def mock_request():
    """Fixture para crear una solicitud simulada."""
    request = MagicMock(spec=Request)
    request.headers = {}
    return request


@pytest.fixture
def mock_settings(monkeypatch):
    """Fixture para simular la configuración de servicios."""
    # Crear una clase MockSettings que simule el comportamiento de Settings
    class MockSettings:
        @property
        def SERVICES(self):
            return {
                "auth": {
                    "url": "http://localhost:8001",
                    "public_paths": ["login", "register", "health"]
                },
                "dentist": {
                    "url": "http://localhost:8002",
                    "public_paths": ["health"]
                }
            }
    
    # Reemplazar el objeto settings con nuestra versión simulada
    mock_settings_obj = MockSettings()
    monkeypatch.setattr("app.api.router.settings", mock_settings_obj)
    return mock_settings_obj


class TestServiceProxy:
    """Pruebas para la función service_proxy."""

    @pytest.mark.asyncio
    async def test_service_not_found(self, mock_request):
        """Prueba que una solicitud a un servicio inexistente devuelva 404."""
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as excinfo:
            await service_proxy("nonexistent", "path", mock_request)
        
        assert excinfo.value.status_code == 404
        assert "no encontrado" in excinfo.value.detail

    @pytest.mark.asyncio
    @patch("app.api.router.forward_request_to_service", new_callable=AsyncMock)
    async def test_public_path_no_auth(self, mock_forward, mock_request, mock_settings):
        """Prueba que una solicitud a una ruta pública se reenvíe sin verificar token."""
        # Configurar
        mock_forward.return_value = {"status": "ok"}
        
        # Ejecutar
        result = await service_proxy("auth", "login", mock_request)
        
        # Verificar
        assert result == {"status": "ok"}
        mock_forward.assert_called_once_with(mock_request, "http://localhost:8001")

    @pytest.mark.asyncio
    @patch("app.api.router.verify_token", new_callable=AsyncMock)
    @patch("app.api.router.forward_request_to_service", new_callable=AsyncMock)
    async def test_private_path_with_auth(self, mock_forward, mock_verify, mock_request, mock_settings):
        """Prueba que una solicitud a una ruta privada con token válido se reenvíe."""
        # Configurar
        mock_verify.return_value = {"user_id": "123"}
        mock_forward.return_value = {"status": "ok"}
        
        # Ejecutar
        result = await service_proxy("dentist", "appointments", mock_request)
        
        # Verificar
        mock_verify.assert_called_once_with(mock_request)
        mock_forward.assert_called_once_with(mock_request, "http://localhost:8002")
        assert result == {"status": "ok"}

    @pytest.mark.asyncio
    @patch("app.api.router.verify_token", side_effect=HTTPException(status_code=401, detail="Token inválido"))
    async def test_private_path_without_auth(self, mock_verify, mock_request, mock_settings):
        """Prueba que una solicitud a una ruta privada sin token sea rechazada."""
        # Ejecutar y verificar
        with pytest.raises(HTTPException) as excinfo:
            await service_proxy("dentist", "appointments", mock_request)
        
        assert excinfo.value.status_code == 401
        assert "Token inválido" in excinfo.value.detail
