import logging
import os
import sys
from pathlib import Path

import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from blob_utils.blob_utils import create_container,delete_blob,download_blob,upload_blob,read_blobs
import service.indexer as service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def http_trigger_blob_list(req: func.HttpRequest) -> func.HttpResponse:
    """List blobs in a specified container and directory."""
    container_name = req.params.get("container")
    container_dir = req.params.get("blob_src_dir", "")
    if not container_name:
        return func.HttpResponse("Please pass a container name.", status_code=400)

    blobs = read_blobs(container_name, container_dir)
    return func.HttpResponse(f"Blobs in container '{container_name}': {blobs}")

def http_trigger_cvt_pdf2json_blobs(req: func.HttpRequest) -> func.HttpResponse:
    """Convert PDFs to JSON and Markdown using Azure Document Intelligence."""
    container = req.params.get("container")
    src = req.params.get("blob_src_dir")
    print("=== DEBUG PARAMS ===")
    print("container:", container)
    print("blob_src_dir:", src)

    if not all([container, src]):
        return func.HttpResponse("Missing parameters: container, blob_src_dir", status_code=400)

    blobs = read_blobs(container, src)
    for blob_src in blobs:
        if blob_src.lower().endswith(".pdf"):
            rel = Path(blob_src).relative_to(src)
            out = Path(src) / rel.stem  
            service.Pdf2JsonConverter(container, blob_src, out).convert_and_upload()

    return func.HttpResponse(f"Converted PDFs from '{src}' to JSON/Markdown.", status_code=200)