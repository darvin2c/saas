import pytest
import uuid
from datetime import datetime, date
from faker import Faker
from app.services.patient_service import PatientService
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from fastapi import HTTPException

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
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient

class TestPatientService:
    """Pruebas para el servicio de pacientes."""
    
    def test_get_patients(self, db_session, test_tenant_id, test_patient):
        """Prueba la obtención de todos los pacientes para un tenant específico."""
        # Crear un paciente adicional para el mismo tenant
        second_patient = Patient(
            id=uuid.uuid4(),
            tenant_id=test_tenant_id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(second_patient)
        
        # Crear un paciente para otro tenant (no debería aparecer en los resultados)
        other_tenant_patient = Patient(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),  # Otro tenant_id
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(other_tenant_patient)
        db_session.commit()
        
        # Obtener pacientes para el tenant de prueba
        patients = PatientService.get_patients(db_session, test_tenant_id)
        
        # Verificar que se obtuvieron los pacientes correctos
        assert len(patients) == 2
        assert all(patient.tenant_id == test_tenant_id for patient in patients)
    
    def test_get_patient(self, db_session, test_tenant_id, test_patient):
        """Prueba la obtención de un paciente específico por ID."""
        # Obtener el paciente de prueba
        patient = PatientService.get_patient(db_session, test_patient.id, test_tenant_id)
        
        # Verificar que se obtuvo el paciente correcto
        assert patient.id == test_patient.id
        assert patient.tenant_id == test_tenant_id
        assert patient.first_name == test_patient.first_name
        assert patient.last_name == test_patient.last_name
    
    def test_get_patient_not_found(self, db_session, test_tenant_id):
        """Prueba la obtención de un paciente que no existe."""
        # Intentar obtener un paciente con un ID que no existe
        with pytest.raises(HTTPException) as excinfo:
            PatientService.get_patient(db_session, uuid.uuid4(), test_tenant_id)
        
        # Verificar que se lanza la excepción correcta
        assert excinfo.value.status_code == 404
        assert "not found" in excinfo.value.detail
    
    def test_get_patient_wrong_tenant(self, db_session, test_patient):
        """Prueba la obtención de un paciente con un tenant incorrecto."""
        # Intentar obtener un paciente con un tenant_id diferente
        wrong_tenant_id = uuid.uuid4()
        
        with pytest.raises(HTTPException) as excinfo:
            PatientService.get_patient(db_session, test_patient.id, wrong_tenant_id)
        
        # Verificar que se lanza la excepción correcta
        assert excinfo.value.status_code == 404
        assert "not found" in excinfo.value.detail
    
    def test_create_patient(self, db_session, test_tenant_id):
        """Prueba la creación de un nuevo paciente."""
        # Datos para crear un nuevo paciente
        patient_data = PatientCreate(
            tenant_id=test_tenant_id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            date_of_birth=date(1985, 5, 15),
            address=fake.address(),
            medical_history="Alergia a la penicilina"
        )
        
        # Crear el paciente
        patient = PatientService.create_patient(db_session, patient_data)
        
        # Verificar que el paciente se creó correctamente
        assert patient.id is not None
        assert patient.tenant_id == test_tenant_id
        assert patient.first_name == patient_data.first_name
        assert patient.last_name == patient_data.last_name
        assert patient.email == patient_data.email
        assert patient.phone == patient_data.phone
        assert patient.date_of_birth == patient_data.date_of_birth
        assert patient.address == patient_data.address
        assert patient.medical_history == patient_data.medical_history
        assert patient.is_active is True
    
    def test_update_patient(self, db_session, test_tenant_id, test_patient):
        """Prueba la actualización de un paciente existente."""
        # Datos para actualizar el paciente
        update_data = PatientUpdate(
            first_name="NuevoNombre",
            email="nuevo.email@example.com",
            medical_history="Actualización del historial médico"
        )
        
        # Actualizar el paciente
        updated_patient = PatientService.update_patient(db_session, test_patient.id, test_tenant_id, update_data)
        
        # Verificar que el paciente se actualizó correctamente
        assert updated_patient.id == test_patient.id
        assert updated_patient.first_name == "NuevoNombre"
        assert updated_patient.email == "nuevo.email@example.com"
        assert updated_patient.medical_history == "Actualización del historial médico"
        # Verificar que los campos no incluidos en la actualización no cambiaron
        assert updated_patient.last_name == test_patient.last_name
        assert updated_patient.phone == test_patient.phone
    
    def test_update_patient_not_found(self, db_session, test_tenant_id):
        """Prueba la actualización de un paciente que no existe."""
        # Datos para actualizar
        update_data = PatientUpdate(first_name="NuevoNombre")
        
        # Intentar actualizar un paciente con un ID que no existe
        with pytest.raises(HTTPException) as excinfo:
            PatientService.update_patient(db_session, uuid.uuid4(), test_tenant_id, update_data)
        
        # Verificar que se lanza la excepción correcta
        assert excinfo.value.status_code == 404
        assert "not found" in excinfo.value.detail
    
    def test_delete_patient(self, db_session, test_tenant_id, test_patient):
        """Prueba la eliminación de un paciente."""
        # Eliminar el paciente
        deleted_patient = PatientService.delete_patient(db_session, test_patient.id, test_tenant_id)
        
        # Verificar que el paciente se marcó como inactivo
        assert deleted_patient.is_active is False
        
        # Verificar que el paciente sigue en la base de datos pero inactivo
        patient_in_db = db_session.query(Patient).filter(Patient.id == test_patient.id).first()
        assert patient_in_db is not None
        assert patient_in_db.is_active is False
    
    def test_delete_patient_not_found(self, db_session, test_tenant_id):
        """Prueba la eliminación de un paciente que no existe."""
        # Intentar eliminar un paciente con un ID que no existe
        with pytest.raises(HTTPException) as excinfo:
            PatientService.delete_patient(db_session, uuid.uuid4(), test_tenant_id)
        
        # Verificar que se lanza la excepción correcta
        assert excinfo.value.status_code == 404
        assert "not found" in excinfo.value.detail
