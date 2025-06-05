# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.infrastructure.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def guardar_en_base_de_datos(instancia, session=None):
    """
    Guarda una instancia en la base de datos, utilizando una sesión existente o creando una nueva.
    """
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        session.add(instancia)
        session.commit()
        session.refresh(instancia)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        if close_session:
            session.close()