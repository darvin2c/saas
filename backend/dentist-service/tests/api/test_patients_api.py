import pytest
import uuid
from datetime import date
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from faker import Faker
from app.main import app
from app.models.patient import Patient
from app.services.patient_service import PatientService

# Inicializar Faker
fake = Faker()

@pytest.fixture
def test_tenant_id():
    """Fixture para generar un ID de tenant de prueba."""
    return uuid.uuid4()

@pytest.fixture
def test_patient(db_session, test_tenant_id):
    """Fixture para crear un paciente de prueba."""
    patient = Patient(
        id=uuid.uuid4(),
        tenant_id=test_tenant_id,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.email(),
        phone=fake.phone_number(),
        date_of_birth=date(1990, 1, 1),
        address=fake.address(),
        medical_history="Sin antecedentes médicos relevantes",
        is_active=True
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient

@pytest.fixture
def auth_headers():
    """Fixture para crear headers de autenticación simulados."""
    return {"Authorization": f"Bearer test_token"}

@pytest.fixture
def mock_validate_token():
    """Fixture para simular la validación del token."""
    with patch("app.api.patients.validate_token") as mock:
        mock.return_value = {"sub": "test_user", "tenant_ids": ["test_tenant"]}
        yield mock

class TestPatientsAPI:
    """Pruebas para la API de pacientes."""
    
    def test_get_patients(self, client, db_session, test_tenant_id, test_patient, mock_validate_token):
        """Prueba la obtención de todos los pacientes para un tenant específico."""
        # Configurar el mock para get_tenant_id_from_path
        with patch("app.api.patients.get_tenant_id_from_path", return_value=test_tenant_id):
            # Realizar la solicitud GET
            response = client.get(f"/{test_tenant_id}/patients")
            
            # Verificar la respuesta
            assert response.status_code == 200
            patients = response.json()
            assert len(patients) == 1
            assert patients[0]["id"] == str(test_patient.id)
            assert patients[0]["first_name"] == test_patient.first_name
            assert patients[0]["last_name"] == test_patient.last_name
    
    def test_search_patients(self, client, db_session, test_tenant_id, test_patient, mock_validate_token):
        """Prueba la búsqueda de pacientes por nombre o email."""
        # Configurar el mock para get_tenant_id_from_path
        with patch("app.api.patients.get_tenant_id_from_path", return_value=test_tenant_id):
            # Configurar el mock para search_patients
            with patch.object(
                PatientService, 
                "search_patients", 
                return_value=[test_patient]
            ) as mock_search:
                # Realizar la solicitud GET con parámetro de búsqueda
                response = client.get(f"/{test_tenant_id}/patients/search?query={test_patient.first_name}")
                
                # Verificar la respuesta
                assert response.status_code == 200
                patients = response.json()
                assert len(patients) == 1
                assert patients[0]["id"] == str(test_patient.id)
                
                # Verificar que se llamó al método search_patients con los parámetros correctos
                mock_search.assert_called_once_with(
                    db_session, test_tenant_id, test_patient.first_name, 0, 100
                )
    
    def test_get_patient(self, client, db_session, test_tenant_id, test_patient, mock_validate_token):
        """Prueba la obtención de un paciente específico por ID."""
        # Configurar el mock para get_tenant_id_from_path
        with patch("app.api.patients.get_tenant_id_from_path", return_value=test_tenant_id):
            # Realizar la solicitud GET
            response = client.get(f"/{test_tenant_id}/patients/{test_patient.id}")
            
            # Verificar la respuesta
            assert response.status_code == 200
            patient = response.json()
            assert patient["id"] == str(test_patient.id)
            assert patient["first_name"] == test_patient.first_name
            assert patient["last_name"] == test_patient.last_name
    
    def test_get_patient_not_found(self, client, db_session, test_tenant_id, mock_validate_token):
        """Prueba la obtención de un paciente que no existe."""
        # Configurar el mock para get_tenant_id_from_path
        with patch("app.api.patients.get_tenant_id_from_path", return_value=test_tenant_id):
            # Configurar el mock para get_patient para simular que no se encuentra el paciente
            with patch.object(
                PatientService, 
                "get_patient", 
                side_effect=Exception("Patient not found")
            ):
                # Realizar la solicitud GET con un ID que no existe
                non_existent_id = uuid.uuid4()
                response = client.get(f"/{test_tenant_id}/patients/{non_existent_id}")
                
                # Verificar la respuesta
                assert response.status_code == 500  # Podría ser 404 dependiendo de cómo manejes las excepciones
    
    def test_create_patient(self, client, db_session, test_tenant_id, mock_validate_token):
        """Prueba la creación de un nuevo paciente."""
        # Datos para crear un nuevo paciente
        new_patient_data = {
            "tenant_id": str(test_tenant_id),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "date_of_birth": "1985-05-15",
            "address": fake.address(),
            "medical_history": "Alergia a la penicilina"
        }
        
        # Configurar el mock para get_tenant_id_from_path
        with patch("app.api.patients.get_tenant_id_from_path", return_value=test_tenant_id):
            # Configurar el mock para create_patient
            with patch.object(
                PatientService, 
                "create_patient", 
                return_value=Patient(
                    id=uuid.uuid4(),
                    **{k: v for k, v in new_patient_data.items() if k != "date_of_birth"},
                    date_of_birth=date(1985, 5, 15),
                    is_active=True
                )
            ) as mock_create:
                # Realizar la solicitud POST
                response = client.post(
                    f"/{test_tenant_id}/patients",
                    json=new_patient_data
                )
                
                # Verificar la respuesta
                assert response.status_code == 201
                patient = response.json()
                assert patient["first_name"] == new_patient_data["first_name"]
                assert patient["last_name"] == new_patient_data["last_name"]
                assert patient["email"] == new_patient_data["email"]
    
    def test_update_patient(self, client, db_session, test_tenant_id, test_patient, mock_validate_token):
        """Prueba la actualización de un paciente existente."""
        # Datos para actualizar el paciente
        update_data = {
            "first_name": "NuevoNombre",
            "email": "nuevo.email@example.com",
            "medical_history": "Actualización del historial médico"
        }
        
        # Configurar el mock para get_tenant_id_from_path
        with patch("app.api.patients.get_tenant_id_from_path", return_value=test_tenant_id):
            # Configurar el mock para update_patient
            updated_patient = test_patient
            updated_patient.first_name = "NuevoNombre"
            updated_patient.email = "nuevo.email@example.com"
            updated_patient.medical_history = "Actualización del historial médico"
            
            with patch.object(
                PatientService, 
                "update_patient", 
                return_value=updated_patient
            ) as mock_update:
                # Realizar la solicitud PUT
                response = client.put(
                    f"/{test_tenant_id}/patients/{test_patient.id}",
                    json=update_data
                )
                
                # Verificar la respuesta
                assert response.status_code == 200
                patient = response.json()
                assert patient["first_name"] == "NuevoNombre"
                assert patient["email"] == "nuevo.email@example.com"
                assert patient["medical_history"] == "Actualización del historial médico"
    
    def test_delete_patient(self, client, db_session, test_tenant_id, test_patient, mock_validate_token):
        """Prueba la eliminación de un paciente."""
        # Configurar el mock para get_tenant_id_from_path
        with patch("app.api.patients.get_tenant_id_from_path", return_value=test_tenant_id):
            # Configurar el mock para delete_patient
            deleted_patient = test_patient
            deleted_patient.is_active = False
            
            with patch.object(
                PatientService, 
                "delete_patient", 
                return_value=deleted_patient
            ) as mock_delete:
                # Realizar la solicitud DELETE
                response = client.delete(f"/{test_tenant_id}/patients/{test_patient.id}")
                
                # Verificar la respuesta
                assert response.status_code == 200
                patient = response.json()
                assert patient["is_active"] is False
