from fastapi import APIRouter, Depends, Security
from uuid import uuid1

from src import (
    cloud_storage,
    crud,
    database,
    dependencies,
    responses,
    requests,
    config
)


class RecordsRoute(APIRouter):
    def __init__(self) -> None:
        super().__init__()

        @self.get(
            "/records/count",
            response_model=responses.CountRecordsResponse,
            dependencies=[Security(dependencies.authenticate)],
        )
        async def count_records(
            url_params: requests.RecordsUrlParams = Depends(),
        ):
            return responses.CountRecordsResponse(
                data={"total_records_count": crud.count_query_records(url_params)}
            )

        @self.get(
            "/records",
            response_model=responses.GetRecordsResponse,
            dependencies=[Security(dependencies.authenticate)],
        )
        async def get_records_csv_link(
            url_params: requests.GetRecordsUrlParams = Depends(),
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
            
        @self.get(
            "/limits",
            response_model=responses.LimitsResponse,
            dependencies=[Security(dependencies.authenticate)],
        )
        async def get_limits():

            return responses.LimitsResponse(
                data={
                    "MAX_AREA_DEGREES": config.MAX_AREA_DEGREES,
                    "MAX_TIMESTAMP_DURATION_HOURS": config.MAX_TIMESTAMP_DURATION_HOURS
                }
            )
