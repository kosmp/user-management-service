from pydantic import BaseModel, constr


class ValidatedGroupName(BaseModel):
    group_name: constr(min_length=1, max_length=15)
