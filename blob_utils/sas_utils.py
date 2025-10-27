from azure.storage.blob import generate_blob_sas, BlobSasPermissions, BlobServiceClient
from datetime import datetime, timedelta
import os
import json

# 加载 local.settings.json 中的环境变量
with open("local.settings.json", "r") as f:
    settings = json.load(f)

# 取出 Values 部分
values = settings.get("Values", {})

# 写入到系统环境变量
for key, value in values.items():
    os.environ[key] = value

def generate_sas_url(container_name: str, blob_name: str, expiry_hours: int = 1):
    """
    生成指定文件的 SAS URL，有效期默认为 1 小时
    """
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    account_name = blob_service_client.account_name

    # 生成 SAS Token
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
    )

    # 拼接完整 URL
    sas_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    return sas_url

container_name = "testfiles"
blob_name = "travelguide_epos_platinum_SompoJapan.pdf"
# blob_name = "GO領収書_20250618_1352.pdf"

sas_url = generate_sas_url(container_name, blob_name, expiry_hours=2)
print("✅ SAS URL 生成成功：", sas_url)