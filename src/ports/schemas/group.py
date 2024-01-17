from pydantic import BaseModel, constr, UUID4, ConfigDict
from datetime import datetime


class CreateGroupModel(BaseModel):
    group_name: constr(min_length=1, max_length=15)


GroupNameType = CreateGroupModel.__annotations__["group_name"]


class GroupResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: constr(min_length=1, max_length=15)
    created_at: datetime
