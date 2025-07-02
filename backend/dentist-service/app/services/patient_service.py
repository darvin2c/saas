from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.models.patient import Patient, PatientGuardian
from app.schemas.patient import PatientCreate, PatientUpdate, PatientGuardianCreate, PatientGuardianUpdate
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
    
    # Patient Guardian methods
    @staticmethod
    def get_patient_guardians(db: Session, patient_id: UUID) -> List[PatientGuardian]:
        """
        Get all guardians for a specific patient.
        """
        return db.query(PatientGuardian).filter(PatientGuardian.patient_id == patient_id).all()
    
    @staticmethod
    def get_guardian_patients(db: Session, guardian_id: UUID) -> List[PatientGuardian]:
        """
        Get all patients for a specific guardian.
        """
        return db.query(PatientGuardian).filter(PatientGuardian.guardian_id == guardian_id).all()
    
    @staticmethod
    def get_patient_guardian(db: Session, patient_id: UUID, guardian_id: UUID) -> PatientGuardian:
        """
        Get a specific patient-guardian relationship.
        """
        guardian_relation = db.query(PatientGuardian).filter(
            PatientGuardian.patient_id == patient_id,
            PatientGuardian.guardian_id == guardian_id
        ).first()
        
        if not guardian_relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Guardian relationship not found for patient {patient_id} and guardian {guardian_id}"
            )
        return guardian_relation
    
    @staticmethod
    def create_patient_guardian(db: Session, guardian_data: PatientGuardianCreate) -> PatientGuardian:
        """
        Create a new patient-guardian relationship.
        """
        # Verify that both patient and guardian exist
        patient = db.query(Patient).filter(Patient.id == guardian_data.patient_id).first()
        guardian = db.query(Patient).filter(Patient.id == guardian_data.guardian_id).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {guardian_data.patient_id} not found"
            )
            
        if not guardian:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Guardian with ID {guardian_data.guardian_id} not found"
            )
        
        # Check if the relationship already exists
        existing_relation = db.query(PatientGuardian).filter(
            PatientGuardian.patient_id == guardian_data.patient_id,
            PatientGuardian.guardian_id == guardian_data.guardian_id
        ).first()
        
        if existing_relation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Guardian relationship already exists between patient {guardian_data.patient_id} and guardian {guardian_data.guardian_id}"
            )
        
        db_guardian_relation = PatientGuardian(**guardian_data.model_dump())
        db.add(db_guardian_relation)
        db.commit()
        db.refresh(db_guardian_relation)
        return db_guardian_relation
    
    @staticmethod
    def update_patient_guardian(db: Session, patient_id: UUID, guardian_id: UUID, guardian_data: PatientGuardianUpdate) -> PatientGuardian:
        """
        Update an existing patient-guardian relationship.
        """
        guardian_relation = PatientService.get_patient_guardian(db, patient_id, guardian_id)
        
        # Update only the fields that are provided
        update_data = guardian_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(guardian_relation, key, value)
        
        db.commit()
        db.refresh(guardian_relation)
        return guardian_relation
    
    @staticmethod
    def delete_patient_guardian(db: Session, patient_id: UUID, guardian_id: UUID) -> None:
        """
        Delete a patient-guardian relationship.
        """
        guardian_relation = PatientService.get_patient_guardian(db, patient_id, guardian_id)
        db.delete(guardian_relation)
        db.commit()
