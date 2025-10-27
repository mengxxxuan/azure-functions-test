import json
import logging
import azure.functions as func
from blob_utils.blob_utils import create_container, ensure_folder_exists  # 复用你的工具函数

logger = logging.getLogger(__name__)

def http_trigger_create_container(req: func.HttpRequest) -> func.HttpResponse:
    """
    创建新的 Container，可选创建文件夹。
    调用示例:
      GET http://localhost:7071/api/HttpTriggerCreateContainer?container=my-container&folder=my-folder
    """
    try:
        # 从 URL 参数中读取
        container_name = req.params.get("container")
        folder_name = req.params.get("folder")

        if not container_name:
            return func.HttpResponse(
                json.dumps({"error": "Missing required parameter: container"}),
                mimetype="application/json",
                status_code=400
            )

        # 创建 container
        create_container(container_name)
        msg = f"Container '{container_name}' created or already exists."

        # 可选创建“文件夹”
        if folder_name:
            ensure_folder_exists(container_name, folder_name)
            msg += f" Folder '{folder_name}' ensured."

        logger.info(msg)
        return func.HttpResponse(
            json.dumps({"message": msg}),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error creating container/folder: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )