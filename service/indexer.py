import os
import base64
import sys
import json

from abc import ABC, abstractclassmethod
from pathlib import Path
from io import BytesIO

from openai import AzureOpenAI
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
import pdfplumber

from blob_utils.blob_utils import upload_blob, download_blob, ensure_folder_exists

class BaseConverter(ABC):
    def __init__(self, 
                 container_name: str,
                 blob_src_path: str | Path,
                 blob_dst_path: str | Path,
                 ):
        super().__init__()
        if not isinstance(container_name, str):
            raise TypeError(f"container_name must be str, got {type(container_name)}")
        if not isinstance(blob_src_path, (str, Path)):
            raise TypeError(f"blob_src_path must be str or Path, got {type(blob_src_path)}")
        if not isinstance(blob_dst_path, (str, Path)):
            raise TypeError(f"blob_dst_path must be str or Path, got {type(blob_dst_path)}")
        
        self.container_name = container_name
        self.blob_src_path = blob_src_path
        self.blob_dst_path = blob_dst_path
    
    @classmethod
    @abstractclassmethod
    def convert_and_upload(self):
        pass

class Pdf2JsonConverter(BaseConverter):
    """Use Azure Document Intelligence to convert PDF to JSON and upload to blob storage."""
    def __init__(self, container_name: str, blob_src_path: str | Path, blob_dst_path: str | Path):
        super().__init__(container_name, blob_src_path, blob_dst_path)
        self.endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
        self.key = os.environ["DOCUMENT_INTELLIGENCE_KEY"]
    
    def convert_and_upload(self):
        # Read PDF file from blob/container/path
        file_bytes = download_blob(self.container_name, self.blob_src_path, None)
        # Get Document Intelligence result
        result = self._custom_converter(file_bytes)
        self._upload_json_and_markdown(result)


    def _custom_converter(self,pdf_bytes: bytes) -> str:
        client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            AnalyzeDocumentRequest(bytes_source=pdf_bytes),
            features=["ocrHighResolution"],
            output_content_format="markdown"
        )
        result = poller.result()
        return result
    
    def _upload_json_and_markdown(self, result):
        src_path = Path(self.blob_src_path)
        parent_dir = src_path.parent
        json_dir = parent_dir / "json"
        md_dir = parent_dir / "markdown" 
        ensure_folder_exists(self.container_name, json_dir)
        ensure_folder_exists(self.container_name, md_dir)

        json_blob_path = json_dir / f"{src_path.stem}.json"
        md_blob_path = md_dir / f"{src_path.stem}.md"

        upload_blob(
            self.container_name,
            None,
            json.dumps(result.as_dict(), ensure_ascii=False, indent=2).encode("utf-8"),
            json_blob_path.as_posix(),
            {"converted": "true", "format": "json"}
        )

        upload_blob(
            self.container_name,
            None,
            result.content.encode("utf-8"),
            md_blob_path.as_posix(),
            {"converted": "true", "format": "markdown"}
        )
        print(f"✅ Uploaded JSON → {json_blob_path}")
        print(f"✅ Uploaded Markdown → {md_blob_path}")