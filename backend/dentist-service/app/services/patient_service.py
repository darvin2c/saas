from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.filters.patient_filter import PatientFilter


class PatientService:
    @staticmethod
    def get_patients(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        Get all patients for a specific tenant with pagination.
        """
        return db.query(Patient).filter(Patient.tenant_id == tenant_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def filter_patients(db: Session, tenant_id: UUID, patient_filter: PatientFilter) -> List[Patient]:
        """
        Filter patients using fastapi-filter.
        """
        query = db.query(Patient).filter(Patient.tenant_id == tenant_id)
        query = patient_filter.filter(query)
        return patient_filter.sort(query).all()
    
    @staticmethod
    def get_patient(db: Session, patient_id: UUID, tenant_id: UUID) -> Patient:
        """
        Get a specific patient by ID for a tenant.
        """
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.tenant_id == tenant_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        return patient
    
    @staticmethod
    def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
        """
        Create a new patient.
        """
        db_patient = Patient(**patient_data.model_dump())
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    
    @staticmethod
    def update_patient(db: Session, patient_id: UUID, tenant_id: UUID, patient_data: PatientUpdate) -> Patient:
        """
        Update an existing patient.
        """
        patient = PatientService.get_patient(db, patient_id, tenant_id)
        
        # Update only the fields that are provided
        update_data = patient_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(patient, key, value)
        
        db.commit()
        db.refresh(patient)
        return patient
    
    @staticmethod
    def delete_patient(db: Session, patient_id: UUID, tenant_id: UUID) -> Patient:
        """
        Delete a patient (soft delete by setting is_active to False).
        """
        patient = PatientService.get_patient(db, patient_id, tenant_id)
        patient.is_active = False
        db.commit()
        db.refresh(patient)
        return patient
    
    @staticmethod
    def hard_delete_patient(db: Session, patient_id: UUID, tenant_id: UUID) -> None:
        """
        Permanently delete a patient from the database.
        """
        patient = PatientService.get_patient(db, patient_id, tenant_id)
        db.delete(patient)
        db.commit()
    
    @staticmethod
    def search_patients(
        db: Session, 
        tenant_id: UUID, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Patient]:
        """
        Search for patients by name or email.
        """
        search = f"%{query}%"
        return db.query(Patient).filter(
            Patient.tenant_id == tenant_id,
            (
                Patient.first_name.ilike(search) |
                Patient.last_name.ilike(search) |
                Patient.email.ilike(search)
            )
        ).offset(skip).limit(limit).all()
