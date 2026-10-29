from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

# Import all models to register them with Base.metadata
# This must happen after Base is defined
def _register_models():
    from ..models import user, case, evidence  # noqa: F401

_register_models()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
