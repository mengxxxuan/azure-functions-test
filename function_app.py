import azure.functions  as func
from router.indexer_router import http_trigger_blob_list, http_trigger_cvt_pdf2json_blobs

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="HttpTriggerReadBlobs")
def read_blobs_route(req: func.HttpRequest) -> func.HttpResponse:
    return http_trigger_blob_list(req)

@app.route(route="HttpTriggerPdf2Json")
def pdf2json_route(req: func.HttpRequest) -> func.HttpResponse:
    """Convert PDFs in blob storage to JSON & Markdown using Azure Document Intelligence."""
    return http_trigger_cvt_pdf2json_blobs(req)