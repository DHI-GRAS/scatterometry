from azure.storage.blob import BlobServiceClient

from src import config


blob_service_client = BlobServiceClient.from_connection_string(config.AZURE_STORAGE_CONNECTION_STRING)


def upload_to_cloud_storage(blob_filename, local_file_path=None, file_stream=None):

    with blob_service_client.get_blob_client(
        container=config.AZURE_STORAGE_BLOB_CONTAINER,
        blob=blob_filename
    ) as blob_client:

        if local_file_path:
            with open(file=local_file_path, mode="rb") as data:
                blob_client.upload_blob(data)

        if file_stream:
            blob_client.upload_blob(file_stream)

    return blob_client
