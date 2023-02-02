import pydantic

from .base import BasicResponse


class GetRecordsData(pydantic.BaseModel):
    download_url: pydantic.HttpUrl
    quota_used_bytes: int
    total_records_count: int


class GetRecordsResponse(BasicResponse):
    data: GetRecordsData


class CountRecordsData(pydantic.BaseModel):
    total_records_count: int


class CountRecordsResponse(BasicResponse):
    data: CountRecordsData
