import pydantic

from typing import Optional
from .base import BasicResponse


class GetRecordsData(pydantic.BaseModel):
    download_url: Optional[pydantic.HttpUrl]
    quota_used_bytes: Optional[int]
    total_records_count: int


class GetRecordsResponse(BasicResponse):
    data: GetRecordsData


class CountRecordsData(pydantic.BaseModel):
    total_records_count: int


class CountRecordsResponse(BasicResponse):
    data: CountRecordsData
