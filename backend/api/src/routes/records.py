import geoalchemy2
import sqlalchemy

from fastapi import APIRouter, Depends
from uuid import uuid1

from src import (
    cloud_storage,
    crud,
    database,
    dependencies,
    responses,
    requests,
)


class RecordsRoute(APIRouter):
    def __init__(self) -> None:
        super().__init__()

        @self.get("/records/count", response_model=responses.CountRecordsResponse)
        async def get_records(
            url_params: requests.RecordsUrlParams = Depends(),
            is_authenticated: str = Depends(dependencies.authenticate),
        ):
            return responses.CountRecordsResponse(
                data={"total_records_count": crud.count_query_records(url_params)}
            )

        @self.get("/records", response_model=responses.GetRecordsResponse)
        async def get_records(
            url_params: requests.GetRecordsUrlParams = Depends(),
            is_authenticated: str = Depends(dependencies.authenticate),
        ):
            df, stream = database.query_to_csv_stream(crud.get_query_string(url_params))
            download_url = None
            quota_used_bytes = None
            if df.empty is False:
                blob_client = cloud_storage.upload_to_cloud_storage(
                    f"{uuid1().hex}.csv", file_stream=stream.getvalue()
                )
                download_url = blob_client.url
                quota_used_bytes = blob_client.get_blob_properties().size

            return responses.GetRecordsResponse(
                data={
                    "download_url": download_url,
                    "quota_used_bytes": quota_used_bytes,
                    "total_records_count": df.shape[0],
                }
            )
