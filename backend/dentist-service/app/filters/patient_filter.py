
from typing import Optional
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.patient import Patient


class PatientFilter(Filter):
    """Filtro para el modelo Patient."""
    
    # Filtros exactos
    is_active: Optional[bool] = None
    
    # Filtros de texto
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None
    
    # Búsqueda (usa search_model_fields)
    search: Optional[str] = None
    
    class Constants(Filter.Constants):
        model = Patient
        search_model_fields = ["first_name", "last_name", "email", "phone", "address", "medical_history"]


