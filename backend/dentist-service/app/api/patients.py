from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.patient import Patient, PatientCreate, PatientUpdate
from app.services.patient_service import PatientService
from app.utils.auth import validate_token, get_tenant_id_from_path
from app.filters.patient_filter import get_patient_filter, PatientFilter

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
    user_data: dict = Depends(validate_token)
):
    """
    Get all patients for the specified tenant with pagination.
    """
    patients = PatientService.get_patients(db, tenant_id, skip, limit)
    return patients


@router.get("/{tenant_id}/patients/filter", response_model=List[Patient])
def filter_patients(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token),
    patient_filter: PatientFilter = get_patient_filter()
):
    """
    Filter patients using multiple criteria.
    
    This endpoint allows filtering patients by various fields and operators:
    - Exact matches: id, tenant_id, is_active, first_name, last_name, email, etc.
    - Text search with LIKE: first_name__like, last_name__like, email__like, etc.
    - Date ranges: date_of_birth__gte, date_of_birth__lte, created_at__gte, etc.
    - Sorting: order_by=["last_name", "-first_name"] (use - for descending order)
    
    Example: /tenants/123/patients/filter?first_name__like=Jo&is_active=true&order_by=["last_name"]
    """
    # Ensure tenant_id filter matches the path parameter
    if patient_filter.tenant_id is None:
        patient_filter.tenant_id = tenant_id
    elif patient_filter.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID in filter must match the tenant ID in the path"
        )
    
    return PatientService.filter_patients(db, tenant_id, patient_filter)


@router.get("/{tenant_id}/patients/search", response_model=List[Patient])
def search_patients(
    tenant_id: UUID = Depends(get_tenant_id_from_path),
    query: str = Query(..., description="Texto de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user_data: dict = Depends(validate_token)
):
    """
    Search for patients by name or email.
    """
    patients = PatientService.search_patients(db, tenant_id, query, skip, limit)
    return patients


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
