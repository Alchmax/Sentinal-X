from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Timestamped(OrmBase):
    created_at: datetime | None = None
