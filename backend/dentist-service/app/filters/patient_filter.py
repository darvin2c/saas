from datetime import date
from typing import Optional, List
from uuid import UUID
from fastapi import Depends
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from app.models.patient import Patient


class PatientFilter(Filter):
    """Filtro para el modelo Patient."""
    
    # Filtros exactos
    id: Optional[UUID] = None
    is_active: Optional[bool] = None
    
    # Filtros de texto
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None
    
    # Filtros de texto con operadores like
    first_name__like: Optional[str] = None
    last_name__like: Optional[str] = None
    email__like: Optional[str] = None
    phone__like: Optional[str] = None
    address__like: Optional[str] = None
    medical_history__like: Optional[str] = None
    
    # Filtros de fecha
    date_of_birth: Optional[date] = None
    date_of_birth__gte: Optional[date] = None
    date_of_birth__lte: Optional[date] = None
    created_at__gte: Optional[date] = None
    created_at__lte: Optional[date] = None
    updated_at__gte: Optional[date] = None
    updated_at__lte: Optional[date] = None
    
    # Ordenamiento
    order_by: List[str] = Field(default_factory=lambda: ["last_name", "first_name"])
    
    class Constants(Filter.Constants):
        model = Patient
        ordering_field_name = "order_by"
        search_model_fields = ["first_name", "last_name", "email", "phone", "address", "medical_history"]


# Dependencia para usar en los endpoints
def get_patient_filter():
    """
    Dependencia para obtener un filtro de pacientes.
    """
    return FilterDepends(PatientFilter)
