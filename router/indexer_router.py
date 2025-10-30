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

def http_trigger_document_intelligence(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger to convert document blobs (PDFs) using Azure Document Intelligence and upload structured outputs.

    This function scans a source directory in blob storage for PDF files,
    processes each with Document Intelligence (via DocumentIntelligenceConverter),
    and uploads the converted JSON or Markdown results to the destination directory.

    Query Parameters:
        - container: (str) Name of the blob container.
        - blob_src_dir: (str) Source directory in the container (where PDFs are located).
        - blob_dst_dir: (str) Destination directory to store converted outputs.

    Example:
        /api/HttpTriggerDocIntelligence?container=mycontainer&blob_src_dir=pdfs/raw&blob_dst_dir=pdfs/parsed
    """
    container = req.params.get("container")
    src_dir = req.params.get("blob_src_dir")
    dst_dir = req.params.get("blob_dst_dir")

    if not all([container, src_dir, dst_dir]):
        return func.HttpResponse(
            "Missing parameters: container, blob_src_dir, blob_dst_dir",
            status_code=400
        )

    blobs = read_blobs(container, src_dir)
    for blob_src_path in blobs:
        if not blob_src_path.lower().endswith(".png"):
                logger.info(f"Skipping non-PDF file: {blob_src_path}")
                continue
        blob_src_relative_path = Path(blob_src_path).relative_to(src_dir)
        blob_dst_path = Path(dst_dir) / blob_src_relative_path.with_suffix(".json")
        converter = service.DocumentIntelligenceConverter(
                container_name=container,
                blob_src_path=blob_src_path,
                blob_dst_path=blob_dst_path
            )
        converter.convert_and_upload()

    return func.HttpResponse(f"Converted PDFs from '{src_dir}' to JSON/Markdown.", status_code=200)

def http_trigger_json_chunk(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger to convert JSON blobs into chunked JSONs using LangChain splitter.

    Query Parameters:
        - container: Blob container name.
        - blob_src_dir: Source directory containing JSON files.
        - blob_dst_dir: Destination directory for chunked JSON outputs.
        - chunk_size (optional): Max characters per chunk (default: 300)
        - chunk_overlap (optional): Overlap size (default: 50)

    Example:
        /api/HttpTriggerJsonChunk?container=mycontainer&blob_src_dir=json/source&blob_dst_dir=json/chunks&chunk_size=500&chunk_overlap=50
    """
    container = req.params.get("container")
    src_dir = req.params.get("blob_src_dir")
    dst_dir = req.params.get("blob_dst_dir")
    chunk_size = int(req.params.get("chunk_size", 100))
    chunk_overlap = int(req.params.get("chunk_overlap", 20))

    if not all([container, src_dir, dst_dir]):
        return func.HttpResponse(
            "Missing parameters: container, blob_src_dir, blob_dst_dir",
            status_code=400
        )
    
    blobs = read_blobs(container, src_dir)
    for blob_src_path in blobs:
            if not blob_src_path.lower().endswith(".json"):
                logger.info(f"Skipping non-JSON file: {blob_src_path}")
                continue

            blob_src_relative_path = Path(blob_src_path).relative_to(src_dir)
            blob_dst_dir_full = Path(dst_dir) / blob_src_relative_path.parent

            converter = service.JsonChunkConverter(
                container_name=container,
                blob_src_path=blob_src_path,
                blob_dst_dir=blob_dst_dir_full,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            converter.convert_and_upload()
    msg = f"JSON file(s) processed from '{src_dir}' and chunked into '{dst_dir}'."
    return func.HttpResponse(msg, status_code=200)