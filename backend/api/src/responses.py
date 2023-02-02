import enum
import pydantic
from typing import Union, Any


class Statuses(enum.Enum):
    success = "success"
    failure = "failure"


class BasicResponse(pydantic.BaseModel):
    status: Statuses
    errors: Union[list[str], None]
    message: Union[str, None]
    data: Any


def build_response(status=None, errors=None, message=None, data=None):

    if status is None:
        status = Statuses.failure if errors else Statuses.success

    return BasicResponse(status=status, errors=errors, message=message, data=data)
