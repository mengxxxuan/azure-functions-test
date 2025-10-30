import azure.functions  as func
from router.indexer_router import http_trigger_blob_list, http_trigger_document_intelligence,http_trigger_json_chunk
from router.container_router import http_trigger_create_container

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="HttpTriggerReadBlobs")
def read_blobs_route(req: func.HttpRequest) -> func.HttpResponse:
    return http_trigger_blob_list(req)

@app.route(route="HttpTriggerPdf2Json")
def pdf2json_route(req: func.HttpRequest) -> func.HttpResponse:
    """Convert PDFs in blob storage to JSON & Markdown using Azure Document Intelligence."""
    return http_trigger_document_intelligence(req)


@app.route(route="HttpTriggerCreateContainer")
def create_container_route(req: func.HttpRequest) -> func.HttpResponse:
    """Create container (and optional folder) in Blob Storage."""
    return http_trigger_create_container(req)

@app.route(route="HttpTriggerJsonChunk")
def json_chunk_route(req: func.HttpRequest) -> func.HttpResponse:
    """Trigger JSON chunking using LangChain text splitter."""
    return http_trigger_json_chunk(req)