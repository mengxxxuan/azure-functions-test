# from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobServiceClient, ContentSettings
import os

# def upload_file_to_blob(file, file_name):
#     """
#     上传文件到指定 Blob container
#     返回上传后的 Blob URL
#     """
#     connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
#     container_name = os.environ.get("BLOB_CONTAINER_NAME", "mycontainer")

#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#     container_client = blob_service_client.get_container_client(container_name)

#     blob_client = container_client.get_blob_client(file_name)
#     blob_client.upload_blob(file, overwrite=True)

#     blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{file_name}"
#     return blob_url

# def upload_file_to_blob(file, file_name):
#     """
#     上传文件到指定 Blob Container
#     返回上传后的 Blob URL
#     """
#     from azure.storage.blob import BlobServiceClient
#     import os

#     connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
#     container_name = os.environ.get("BLOB_CONTAINER_NAME", "mycontainer")

#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#     container_client = blob_service_client.get_container_client(container_name)

#     blob_client = container_client.get_blob_client(file_name)
#     blob_client.upload_blob(file, overwrite=True)

#     blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{file_name}"
#     return blob_url
def upload_file_to_blob(file_path: str, file_name: str):
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    container_name = os.environ["BLOB_CONTAINER_NAME"]

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

    with open(file_path, "rb") as data:
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type="application/pdf")
        )

    blob_url = blob_client.url
    print(f"✅ 上传成功: {blob_url}")
    return blob_url