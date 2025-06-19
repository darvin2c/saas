from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Configurar el esquema auth por defecto para todos los modelos
metadata = MetaData(schema='auth')

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Usar el metadata con el esquema auth configurado
Base = declarative_base(metadata=metadata)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
