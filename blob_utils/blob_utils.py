
import logging
import os
import json
import time
from pathlib import Path
from io import BytesIO
from azure.core.exceptions import ResourceExistsError
from azure.identity import AzureCliCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

if os.path.exists("local.settings.json"):
    with open("local.settings.json") as f:
        settings = json.load(f).get("Values", {})
        for key, value in settings.items():
            os.environ[key] = value

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

credential = DefaultAzureCredential()  # For deployment

# Initialize Service Client
blob_service_client = BlobServiceClient(
    account_url=str(os.getenv("BLOB_ENDPOINT")),
    credential=credential
)

def create_container(blob_container_name: str) -> None:
    """Create a container if it does not exist.

    Args:
        blob_container_name (str): The name of the container to create.
    Returns:
        None
    """
    try:
        blob_service_client.create_container(blob_container_name)
        message = f"Container '{blob_container_name}' created."
        logger.info(message)
    except ResourceExistsError:
        message = f"Container '{blob_container_name}' already exists."
        logger.warning(message)

def upload_blob(
    blob_container_name: str,
    file_src_path: Path | None,
    file_src_bytes: bytes | None,
    blob_dst_path: str | Path,
    metadata: dict | None = None
) -> None:
    """Upload a file or bytes to blob storage (auto-handles large files & timeouts)."""

    blob_client = blob_service_client.get_blob_client(
        container=blob_container_name,
        blob=str(blob_dst_path)
    )

    start_time = time.time()

    # Determine data source
    if file_src_path:
        with open(file_src_path, "rb") as data:
            data_bytes = data.read()
    elif file_src_bytes:
        data_bytes = file_src_bytes
    else:
        raise ValueError("Either file_src_path or file_src_bytes must be provided.")

    size_mb = len(data_bytes) / 1024 / 1024
    print(f"📦 Uploading {blob_dst_path} ({size_mb:.2f} MB) to container '{blob_container_name}'...")

    # Use stream for safer multi-threaded upload
    stream = BytesIO(data_bytes)

    # Upload with retries and larger timeout
    try:
        blob_client.upload_blob(
            data=stream,
            overwrite=True,
            metadata=metadata,
            max_concurrency=4,    # enable parallel chunk upload
            length=len(data_bytes),
            timeout=900           # 15 minutes
        )
        elapsed = time.time() - start_time
        logger.info(f"✅ Uploaded blob to {blob_container_name}/{blob_dst_path} in {elapsed:.2f} seconds ({size_mb:.2f} MB).")
    except Exception as e:
        logger.error(f"❌ Failed to upload {blob_dst_path}: {e}")
        raise
# def upload_blob(
#     blob_container_name: str,
#     file_src_path: Path | None,
#     file_src_bytes: bytes | None,
#     blob_dst_path: str | Path,
#     metadata: dict | None = None
# ) -> None:
#     """Upload a file or bytes to blob storage.

#     Args:
#         blob_container_name (str): Container name.
#         file_src_path (Path | None): Local source file path (if uploading from file).
#         file_src_bytes (bytes | None): Source bytes (if uploading from memory).
#         blob_dst_path (str | Path): Target blob path.
#         metadata (dict | None): Optional metadata.
#     Returns:
#         None
#     """
#     blob_client = blob_service_client.get_blob_client(
#         container=blob_container_name,
#         blob=str(blob_dst_path)
#     )

#     if file_src_path:
#         with open(file_src_path, "rb") as data:
#             blob_client.upload_blob(data, overwrite=True, metadata=metadata,timeout=600)
#     elif file_src_bytes:
#         blob_client.upload_blob(file_src_bytes, overwrite=True, metadata=metadata,timeout=600)
#     else:
#         raise ValueError("Either file_src_path or file_src_bytes must be provided.")

#     logger.info(f"Uploaded blob to {blob_container_name}/{blob_dst_path}")

def download_blob(
    blob_container_name: str,
    blob_src_path: str | Path,
    file_dst_path: Path | None
) -> bytes | None:
    """Download a blob file from storage.

    Args:
        blob_container_name (str): Container name.
        blob_src_path (str | Path): Source blob path.
        file_dst_path (Path | None): Local file path (optional, if saving to disk).
    Returns:
        bytes | None: The downloaded file bytes if not saved to disk.
    """
    blob_client = blob_service_client.get_blob_client(
        container=blob_container_name,
        blob=str(blob_src_path)
    )

    stream = blob_client.download_blob()
    file_bytes = stream.readall()

    if file_dst_path:
        file_dst_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_dst_path, "wb") as file:
            file.write(file_bytes)
        logger.info(f"Downloaded blob to local file {file_dst_path}")
        return None

    logger.info(f"Downloaded blob {blob_container_name}/{blob_src_path} to memory.")
    return file_bytes

def read_blobs(blob_container_name: str, prefix: str | None = None) -> list[str]:
    """List all blobs in a container.

    Args:
        blob_container_name (str): Container name.
        prefix (str | None): Optional prefix filter.
    Returns:
        list[str]: A list of blob names.
    """
    container_client = blob_service_client.get_container_client(blob_container_name)
    blobs = container_client.list_blobs(name_starts_with=prefix)
    blob_names = [blob.name for blob in blobs]
    logger.info(f"Listed {len(blob_names)} blobs from '{blob_container_name}' (prefix='{prefix}')")
    return blob_names


def delete_blob(blob_container_name: str, blob_path: str | Path) -> None:
    """Delete a blob file from storage.

    Args:
        blob_container_name (str): Container name.
        blob_path (str | Path): Path of the blob to delete.
    Returns:
        None
    """
    blob_client = blob_service_client.get_blob_client(
        container=blob_container_name,
        blob=str(blob_path)
    )
    blob_client.delete_blob(delete_snapshots="include")
    logger.info(f"Deleted blob {blob_container_name}/{blob_path}")


def ensure_folder_exists(blob_container_name: str, folder_path: str | Path):
    """Ensure a virtual folder (prefix) exists in Azure Blob Storage.

    Args:
        blob_container_name (str): Blob Container name
        folder_path (str | Path): abs path。
    """
    folder_path = Path(folder_path)
    blob_client = blob_service_client.get_blob_client(
        container=blob_container_name,
        blob=(folder_path / ".keep").as_posix()
    )

    try:
        blob_client.upload_blob(b"", overwrite=False)
        logger.info(f"📁 Created folder placeholder: {folder_path}/.keep")
    except ResourceExistsError:
        logger.debug(f"Folder already exists: {folder_path}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to ensure folder {folder_path}: {e}")