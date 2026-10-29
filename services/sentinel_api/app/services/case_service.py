import uuid
from datetime import UTC

from sqlalchemy.orm import Session

from ..models.case import Case
from ..schemas.case import CaseCreate, CaseUpdate


def create_case(db: Session, owner_id: str, data: CaseCreate) -> Case:
    case = Case(
        id=str(uuid.uuid4()),
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        tags=",".join(data.tags),
        owner_id=owner_id,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def get_case(db: Session, case_id: str) -> Case | None:
    return db.query(Case).filter(Case.id == case_id).first()


def list_cases(
    db: Session,
    owner_id: str,
    query: str = "",
    status: str = "",
    limit: int = 50,
    offset: int = 0,
):
    q = db.query(Case).filter(Case.owner_id == owner_id)
    if query:
        q = q.filter(
            Case.title.ilike(f"%{query}%") | Case.description.ilike(f"%{query}%")
        )
    if status:
        q = q.filter(Case.status == status)
    total = q.count()
    items = q.order_by(Case.created_at.desc()).offset(offset).limit(limit).all()
    return items, total


def update_case(db: Session, case: Case, data: CaseUpdate) -> Case:
    if data.title is not None:
        case.title = data.title
    if data.description is not None:
        case.description = data.description
    if data.status is not None:
        case.status = data.status
    if data.priority is not None:
        case.priority = data.priority
    if data.tags is not None:
        case.tags = ",".join(data.tags)
    from datetime import datetime

    case.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(case)
    return case


def archive_case(db: Session, case: Case) -> Case:
    from datetime import datetime

    case.status = "archived"
    case.archived_at = datetime.now(UTC)
    db.commit()
    db.refresh(case)
    return case


def delete_case(db: Session, case: Case):
    db.delete(case)
    db.commit()
