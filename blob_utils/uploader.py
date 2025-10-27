import os
import json
from azure.storage.blob import BlobServiceClient, ContentSettings

def load_local_settings():
    """
    从 local.settings.json 加载配置
    """
    try:
        settings_path = "local.settings.json"
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        return settings.get("Values", {})
    except FileNotFoundError:
        print(f"❌ 找不到配置文件: {settings_path}")
        return {}
    except json.JSONDecodeError:
        print(f"❌ 配置文件格式错误: {settings_path}")
        return {}

def get_connection_string():
    """
    获取连接字符串，优先从环境变量，其次从 local.settings.json
    """
    # 首先尝试环境变量
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.environ.get("BLOB_CONTAINER_NAME")
    
    # 如果环境变量中没有，尝试从 local.settings.json 读取
    if not connection_string or not container_name:
        settings = load_local_settings()
        connection_string = connection_string or settings.get("AZURE_STORAGE_CONNECTION_STRING")
        container_name = container_name or settings.get("BLOB_CONTAINER_NAME")
    
    return connection_string, container_name

def upload_folder_to_blob(local_folder_path: str, blob_folder_path: str):
    """
    上传本地文件夹中的所有文件到 Azure Blob Storage 的指定文件夹
    
    Args:
        local_folder_path (str): 本地文件夹路径
        blob_folder_path (str): Blob Storage 中的目标文件夹路径
    """
    # 获取连接字符串和容器名称
    connection_string, container_name = get_connection_string()
    
    if not connection_string:
        print("❌ 未找到 AZURE_STORAGE_CONNECTION_STRING")
        return
    
    if not container_name:
        print("❌ 未找到 BLOB_CONTAINER_NAME")
        return
    
    print(f"🔗 使用容器: {container_name}")
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # 确保 blob_folder_path 以 '/' 结尾
    if blob_folder_path and not blob_folder_path.endswith('/'):
        blob_folder_path += '/'
    
    # 获取所有文件列表
    files = [f for f in os.listdir(local_folder_path) if os.path.isfile(os.path.join(local_folder_path, f))]
    
    if not files:
        print("📁 文件夹中没有找到任何文件")
        return
    
    print(f"📂 找到 {len(files)} 个文件，开始上传...")
    
    # 遍历本地文件夹中的所有文件
    for file_name in files:
        local_file_path = os.path.join(local_folder_path, file_name)
        
        try:
            # 在 Blob Storage 中创建完整的文件路径
            blob_file_path = blob_folder_path + file_name
            
            # 获取 blob client
            blob_client = blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_file_path
            )
            
            # 根据文件扩展名设置内容类型
            content_type = get_content_type(file_name)
            
            # 上传文件
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    content_settings=ContentSettings(content_type=content_type)
                )
            
            blob_url = blob_client.url
            print(f"✅ 上传成功: {file_name} -> {blob_url}")
            
        except Exception as e:
            print(f"❌ 上传失败 {file_name}: {str(e)}")
    
    print(f"🎉 文件上传完成！成功上传了 {len(files)} 个文件")

def get_content_type(file_name: str) -> str:
    """
    根据文件扩展名返回对应的内容类型
    """
    extension = os.path.splitext(file_name)[1].lower()
    
    content_types = {
        # 文档类型
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.rtf': 'application/rtf',
        
        # Excel 文件类型
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
        '.xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
        
        # Word 文件类型
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        
        # 图像类型
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.svg': 'image/svg+xml',
        
        # 其他常见类型
        '.html': 'text/html',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.zip': 'application/zip',
        '.csv': 'text/csv',
    }
    
    return content_types.get(extension, 'application/octet-stream')

# 使用示例
if __name__ == "__main__":
    local_folder = "/Users/mengxuan/Downloads/files_tobe_uploaded"  # 本地文件夹路径
    blob_folder = "documents"       # Blob Storage 中的目标文件夹
    
    upload_folder_to_blob(local_folder, blob_folder)
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
# def upload_file_to_blob(file_path: str, file_name: str):
#     connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
#     container_name = os.environ["BLOB_CONTAINER_NAME"]

#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#     blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

#     with open(file_path, "rb") as data:
#         blob_client.upload_blob(
#             data,
#             overwrite=True,
#             content_settings=ContentSettings(content_type="application/pdf")
#         )

#     blob_url = blob_client.url
#     print(f"✅ 上传成功: {blob_url}")
#     return blob_url
