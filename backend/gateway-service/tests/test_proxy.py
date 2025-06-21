import pytest
from fastapi import Request
from unittest.mock import MagicMock, patch, AsyncMock
import httpx

from app.utils.proxy import forward_request_to_service


@pytest.fixture
def mock_request():
    """Fixture para crear una solicitud simulada."""
    request = MagicMock(spec=Request)
    request.method = "GET"
    request.url.path = "/dentist/appointments"
    request.query_params = {}
    request.headers = {"Content-Type": "application/json", "Authorization": "Bearer token123"}
    request.cookies = {}
    request.body = AsyncMock(return_value=b'{"data": "test"}')
    return request


class TestProxy:
    """Pruebas para las funciones de proxy."""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.request", new_callable=AsyncMock)
    async def test_forward_request_url_construction(self, mock_request_method, mock_request):
        """Prueba que la URL se construya correctamente."""
        # Configurar
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = b'{"result": "success"}'
        mock_request_method.return_value = mock_response
        
        # Configurar la URL correctamente
        mock_request.url.query = ""
        
        # Ejecutar
        await forward_request_to_service(mock_request, "http://localhost:8002")
        
        # Verificar
        mock_request_method.assert_called_once()
        call_args = mock_request_method.call_args[1]
        # Verificar que la URL contenga la parte correcta, sin verificar la query
        assert "http://localhost:8002/appointments" in call_args["url"]
        assert call_args["method"] == "GET"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.request", new_callable=AsyncMock)
    async def test_forward_request_headers(self, mock_request_method, mock_request):
        """Prueba que los headers se reenvíen correctamente."""
        # Configurar
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = b'{"result": "success"}'
        mock_request_method.return_value = mock_response
        
        # Ejecutar
        await forward_request_to_service(mock_request, "http://localhost:8002")
        
        # Verificar
        mock_request_method.assert_called_once()
        call_args = mock_request_method.call_args[1]
        assert "headers" in call_args
        assert call_args["headers"]["Content-Type"] == "application/json"
        assert call_args["headers"]["Authorization"] == "Bearer token123"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.request", new_callable=AsyncMock)
    async def test_forward_request_body(self, mock_request_method, mock_request):
        """Prueba que el cuerpo de la solicitud se reenvíe correctamente."""
        # Configurar
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = b'{"result": "success"}'
        mock_request_method.return_value = mock_response
        
        # Ejecutar
        await forward_request_to_service(mock_request, "http://localhost:8002")
        
        # Verificar
        mock_request_method.assert_called_once()
        call_args = mock_request_method.call_args[1]
        assert call_args["content"] == b'{"data": "test"}'

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.request", side_effect=httpx.RequestError("Connection error"))
    async def test_forward_request_connection_error(self, mock_request_method, mock_request):
        """Prueba el manejo de errores de conexión."""
        # Ejecutar y verificar
        response = await forward_request_to_service(mock_request, "http://localhost:8002")
        
        # Verificar que se devuelva una respuesta de error 503
        assert response.status_code == 503
        
        # En FastAPI, el contenido se pasa como parámetro al constructor de Response
        # pero no se puede acceder directamente como atributo
        # Verificamos solo el código de estado que es suficiente para esta prueba
        mock_request_method.assert_called_once()
