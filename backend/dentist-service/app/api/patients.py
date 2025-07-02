from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.patient import Patient, PatientCreate, PatientUpdate, PatientGuardian, PatientGuardianCreate, PatientGuardianUpdate
from app.models.patient import Patient as PatientModel
from app.services.patient_service import PatientService
from app.utils.auth import validate_token, get_tenant_id_from_path
from app.filters.patient_filter import PatientFilter
from fastapi_filter import FilterDepends

router = APIRouter(
    tags=["patients"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{tenant_id}/patients", response_model=List[Patient])
def get_patients(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token),
    patient_filter: PatientFilter = FilterDepends(PatientFilter)
):
    """
    Get all patients for a specific tenant.
    
    Se puede usar de estas formas:
    1. Sin parámetros: Devuelve todos los pacientes
    2. Con search: Busca en los campos definidos en search_model_fields
    3. Con filtros específicos: Filtra por los campos definidos
    4. Con order_by: Ordena los resultados
    """
    query = patient_filter.filter(db.query(PatientModel).filter(PatientModel.tenant_id == tenant_id))
    return query.offset(skip).limit(limit).all()


@router.get("/{tenant_id}/patients/{patient_id}", response_model=Patient)
def get_patient(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    patient_id: UUID = Path(..., description="ID del paciente"),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Get a specific patient by ID.
    """
    return PatientService.get_patient(db, patient_id, tenant_id)


@router.post("/{tenant_id}/patients", response_model=Patient, status_code=status.HTTP_201_CREATED)
def create_patient(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    patient_data: PatientCreate = Depends(),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Create a new patient.
    """
    # Ensure the tenant_id in the request matches the URL tenant_id
    if patient_data.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID mismatch"
        )
    
    return PatientService.create_patient(db, patient_data)


@router.put("/{tenant_id}/patients/{patient_id}", response_model=Patient)
def update_patient(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    patient_id: UUID = Path(..., description="ID del paciente"),
    patient_data: PatientUpdate = Depends(),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Update an existing patient.
    """
    return PatientService.update_patient(db, patient_id, tenant_id, patient_data)


@router.delete("/{tenant_id}/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    patient_id: UUID = Path(..., description="ID del paciente"),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Delete a patient (soft delete).
    """
    PatientService.delete_patient(db, patient_id, tenant_id)
    return None


# Patient Guardian endpoints
@router.get("/{tenant_id}/patients/{patient_id}/guardians", response_model=List[PatientGuardian])
def get_patient_guardians(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    patient_id: UUID = Path(..., description="ID del paciente"),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Get all guardians for a specific patient.
    """
    # Verify that the patient exists and belongs to the tenant
    PatientService.get_patient(db, patient_id, tenant_id)
    return PatientService.get_patient_guardians(db, patient_id)


@router.get("/{tenant_id}/guardians/{guardian_id}/patients", response_model=List[PatientGuardian])
def get_guardian_patients(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    guardian_id: UUID = Path(..., description="ID del guardián"),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Get all patients for a specific guardian.
    """
    # Verify that the guardian exists and belongs to the tenant
    PatientService.get_patient(db, guardian_id, tenant_id)
    return PatientService.get_guardian_patients(db, guardian_id)


@router.get("/{tenant_id}/patients/{patient_id}/guardians/{guardian_id}", response_model=PatientGuardian)
def get_patient_guardian(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    patient_id: UUID = Path(..., description="ID del paciente"),
    guardian_id: UUID = Path(..., description="ID del guardián"),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Get a specific patient-guardian relationship.
    """
    # Verify that both patient and guardian exist and belong to the tenant
    PatientService.get_patient(db, patient_id, tenant_id)
    PatientService.get_patient(db, guardian_id, tenant_id)
    return PatientService.get_patient_guardian(db, patient_id, guardian_id)


@router.post("/{tenant_id}/patients/{patient_id}/guardians", response_model=PatientGuardian, status_code=status.HTTP_201_CREATED)
def create_patient_guardian(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    patient_id: UUID = Path(..., description="ID del paciente"),
    guardian_data: PatientGuardianCreate = Depends(),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Create a new patient-guardian relationship.
    """
    # Verify that the patient_id in the path matches the one in the request body
    if guardian_data.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient ID mismatch between URL and request body"
        )
    
    # Verify that both patient and guardian exist and belong to the tenant
    PatientService.get_patient(db, patient_id, tenant_id)
    PatientService.get_patient(db, guardian_data.guardian_id, tenant_id)
    
    return PatientService.create_patient_guardian(db, guardian_data)


@router.put("/{tenant_id}/patients/{patient_id}/guardians/{guardian_id}", response_model=PatientGuardian)
def update_patient_guardian(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    patient_id: UUID = Path(..., description="ID del paciente"),
    guardian_id: UUID = Path(..., description="ID del guardián"),
    guardian_data: PatientGuardianUpdate = Depends(),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Update an existing patient-guardian relationship.
    """
    # Verify that both patient and guardian exist and belong to the tenant
    PatientService.get_patient(db, patient_id, tenant_id)
    PatientService.get_patient(db, guardian_id, tenant_id)
    
    return PatientService.update_patient_guardian(db, patient_id, guardian_id, guardian_data)


@router.delete("/{tenant_id}/patients/{patient_id}/guardians/{guardian_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_guardian(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    patient_id: UUID = Path(..., description="ID del paciente"),
    guardian_id: UUID = Path(..., description="ID del guardián"),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Delete a patient-guardian relationship.
    """
    # Verify that both patient and guardian exist and belong to the tenant
    PatientService.get_patient(db, patient_id, tenant_id)
    PatientService.get_patient(db, guardian_id, tenant_id)
    
    PatientService.delete_patient_guardian(db, patient_id, guardian_id)
    return None
