import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import case, user  # noqa
from app.schemas.case import CaseCreate
from app.services import case_service

PG_URL = os.getenv("TEST_DATABASE_URL", "")

@pytest.mark.skipif(not PG_URL.startswith("postgresql"), reason="No PG URL")
def test_pg_case_create():
    engine = create_engine(PG_URL)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        # need a user
        import uuid

        from app.core.security import hash_password
        from app.models.user import User
        u = User(id=str(uuid.uuid4()), email="pg@test.com", hashed_password=hash_password("x"))
        db.add(u)
        db.commit()
        c = case_service.create_case(db, u.id, CaseCreate(title="PG Case"))
        assert c.id
        db.delete(c)
        db.delete(u)
        db.commit()
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)