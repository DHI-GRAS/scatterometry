import enum
import pydantic
from typing import Union, Any, Optional


class Statuses(enum.Enum):
    success = "success"
    failure = "failure"


class BasicResponse(pydantic.BaseModel):
    errors: Optional[list[str]]
    status: Optional[Statuses]
    message: Optional[str]
    data: Any

    @pydantic.validator("status")
    def default_status(cls, value, values):
        if value is None:
            value = Statuses.failure if values["errors"] else Statuses.success
        return value
