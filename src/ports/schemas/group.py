from pydantic import BaseModel, constr, UUID5
from datetime import datetime


class CreateGroupModel(BaseModel):
    group_name: constr(min_length=1, max_length=15)


class GroupResponseModel(BaseModel):
    id: UUID5
    name: constr(min_length=1, max_length=15)
    created_at: datetime
