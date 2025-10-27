import azure.functions as func
import datetime
import json
import azure.functions as func
import logging
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField
)
# 索引操作 - 管理索引结构
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField

# 索引器操作 - 管理数据源和索引器  
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField, 
    SearchableField,
    SearchIndexerSkillset,
    SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexer,
    IndexingParameters,
    FieldMapping,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)

# 文档操作 - 上传和搜索文档
from azure.search.documents import SearchClient
import sys
sys.path.append(os.path.dirname(__file__))
from blob_utils.uploader import upload_file_to_blob

app = func.FunctionApp()

# @app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
# def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     name = req.params.get('name')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('name')

#     if name:
#         return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
#     else:
#         return func.HttpResponse(
#              "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
#              status_code=200
#         )

# @app.route(route="create_index", auth_level=func.AuthLevel.FUNCTION)
# def create_index(req: func.HttpRequest) -> func.HttpResponse:
#     """创建PDF RAG搜索索引"""
#     logging.info('开始创建搜索索引...')
#     try:
#         # 从环境变量获取配置
#         search_service_name = os.environ["SEARCH_SERVICE_NAME"]  # ← "meng-test"
#         admin_key = os.environ["SEARCH_ADMIN_KEY"]              # ← 你的密钥
        
#         # 构建搜索服务端点
#         endpoint = f"https://{search_service_name}.search.windows.net"
        
#         # 创建认证客户端
#         credential = AzureKeyCredential(admin_key)
#         search_index_client = SearchIndexClient(endpoint, credential)
        
#         # 为PDF文档定义字段
#         fields = [
#             SimpleField(name="id", type="Edm.String", key=True, filterable=True),
#             SearchableField(name="content", type="Edm.String", searchable=True, analyzer="zh-Hans.microsoft"),
#             SearchableField(name="title", type="Edm.String", filterable=True),
#             SimpleField(name="file_name", type="Edm.String", filterable=True),
#             SimpleField(name="page_number", type="Edm.Int32", filterable=True),
#             SimpleField(name="chunk_id", type="Edm.String", filterable=True)
#         ]
        
#         index_name = req.params.get('index_name', 'pdf-documents')
#         index = SearchIndex(name=index_name, fields=fields)
        
#         # 执行创建
#         result = search_index_client.create_index(index)
        
#         return func.HttpResponse(
#             f"🎉 索引 '{index_name}' 在服务 'meng-test' 中创建成功！\n"
#             f"端点: https://meng-test.search.windows.net\n"
#             f"字段: {[f.name for f in fields]}",
#             status_code=200
#         )
        
#     except Exception as e:
#         logging.error(f"创建索引时出错: {str(e)}")
#         return func.HttpResponse(f"错误: {str(e)}", status_code=500)


# @app.route(route="create_blob_datasource", auth_level=func.AuthLevel.FUNCTION)
# def create_blob_datasource(req: func.HttpRequest) -> func.HttpResponse:
#     """创建 Blob 存储数据源连接"""
#     from azure.search.documents.indexes.models import SearchIndexerDataContainer, SearchIndexerDataSourceConnection
#     from azure.search.documents.indexes import SearchIndexerClient  # ✅ 正确的客户端
    
#     try:
#         search_service_name = os.environ["SEARCH_SERVICE_NAME"]
#         admin_key = os.environ["SEARCH_ADMIN_KEY"]
#         endpoint = f"https://{search_service_name}.search.windows.net"
        
#         credential = AzureKeyCredential(admin_key)
        
#         # ✅ 使用 SearchIndexerClient 而不是 SearchIndexClient
#         indexer_client = SearchIndexerClient(endpoint, credential)
        
#         # 直接从环境变量读取
#         storage_connection_string = os.environ["BLOB_STORAGE_CONNECTION_STRING"]
#         container_name = os.environ["BLOB_CONTAINER_NAME"]
        
#         # 创建数据源配置
#         datasource = SearchIndexerDataSourceConnection(
#             name="pdf-blob-datasource",
#             type="azureblob",
#             connection_string=storage_connection_string,
#             container=SearchIndexerDataContainer(name=container_name)
#         )
        
#         # ✅ 使用正确的客户端创建数据源
#         result = indexer_client.create_data_source_connection(datasource)
        
#         return func.HttpResponse(
#             f"✅ Blob 数据源创建成功！\n"
#             f"数据源名称: pdf-blob-datasource\n"
#             f"容器: {container_name}\n"
#             f"现在你可以创建索引器来处理PDF文件了",
#             status_code=200
#         )
        
#     except Exception as e:
#         return func.HttpResponse(f"创建数据源错误: {str(e)}", status_code=500)

# @app.route(route="create_skillset", auth_level=func.AuthLevel.FUNCTION)
# def create_skillset(req: func.HttpRequest) -> func.HttpResponse:
#     """创建包含 Document Intelligence 的 Skillset"""
#     from azure.search.documents.indexes.models import (
#         SearchIndexerSkillset,
#         OcrSkill,
#         MergeSkill,
#         SplitSkill,
#         EntityRecognitionSkill,
#         LanguageDetectionSkill,
#         InputFieldMappingEntry,
#         OutputFieldMappingEntry
#     )
    
#     try:
#         search_service_name = os.environ["SEARCH_SERVICE_NAME"]
#         admin_key = os.environ["SEARCH_ADMIN_KEY"]
#         endpoint = f"https://{search_service_name}.search.windows.net"
        
#         credential = AzureKeyCredential(admin_key)
#         indexer_client = SearchIndexerClient(endpoint, credential)
        
#         # 定义技能集
#         skillset = SearchIndexerSkillset(
#             name="pdf-processing-skillset",
#             description="PDF文档处理技能集，包含OCR和文本增强",
#             skills=[
#                 # 1. 语言检测
#                 LanguageDetectionSkill(
#                     name="language-detection",
#                     description="检测文档语言",
#                     context="/document",
#                     inputs=[
#                         InputFieldMappingEntry(name="text", source="/document/content")
#                     ],
#                     outputs=[
#                         OutputFieldMappingEntry(name="languageCode", target_name="language")
#                     ]
#                 ),
                
#                 # 2. OCR 技能（从图片提取文字）
#                 OcrSkill(
#                     name="ocr-skill",
#                     description="从图片中提取文字",
#                     context="/document/normalized_images/*",
#                     text_extraction_algorithm="printed",
#                     inputs=[
#                         InputFieldMappingEntry(name="image", source="/document/normalized_images/*")
#                     ],
#                     outputs=[
#                         OutputFieldMappingEntry(name="text", target_name="text")
#                     ]
#                 ),
                
#                 # 3. 合并文本（合并OCR结果和原始文本）
#                 MergeSkill(
#                     name="merge-text",
#                     description="合并OCR文本和原始文本",
#                     context="/document",
#                     inputs=[
#                         InputFieldMappingEntry(name="text", source="/document/content"),
#                         InputFieldMappingEntry(name="itemsToInsert", source="/document/normalized_images/*/text"),
#                         InputFieldMappingEntry(name="offsets", source="/document/normalized_images/*/contentOffset")
#                     ],
#                     outputs=[
#                         OutputFieldMappingEntry(name="mergedText", target_name="merged_content")
#                     ]
#                 ),
                
#                 # 4. 文本分块（适合RAG）
#                 SplitSkill(
#                     name="split-skill",
#                     description="将长文本分成适合RAG的块",
#                     context="/document",
#                     text_split_mode="pages",
#                     maximum_page_length=1000,
#                     inputs=[
#                         InputFieldMappingEntry(name="text", source="/document/merged_content")
#                     ],
#                     outputs=[
#                         OutputFieldMappingEntry(name="textItems", target_name="pages")
#                     ]
#                 )
#             ]
#         )
        
#         # 创建技能集
#         result = indexer_client.create_skillset(skillset)
        
#         return func.HttpResponse(
#             "✅ Skillset 创建成功！包含：语言检测、OCR、文本合并、分块功能",
#             status_code=200
#         )
        
#     except Exception as e:
#         return func.HttpResponse(f"创建Skillset错误: {str(e)}", status_code=500)

# @app.route(route="create_di_skillset", auth_level=func.AuthLevel.FUNCTION)
# def create_di_skillset(req: func.HttpRequest) -> func.HttpResponse:
#     """创建使用 Document Intelligence Layout 和智能分块的 Skillset"""
#     from azure.search.documents.indexes.models import (
#         SearchIndexerSkillset,
#         WebApiSkill,
#         SplitSkill,
#         InputFieldMappingEntry,
#         OutputFieldMappingEntry,
#         SearchIndexerSkillset
#     )
    
#     try:
#         search_service_name = os.environ["SEARCH_SERVICE_NAME"]
#         admin_key = os.environ["SEARCH_ADMIN_KEY"]
#         di_endpoint = os.environ("DOCUMENT_INTELLIGENCE_ENDPOINT")
#         di_key = os.environ("DOCUMENT_INTELLIGENCE_KEY")
        
#         endpoint = f"https://{search_service_name}.search.windows.net"
#         credential = AzureKeyCredential(admin_key)
#         indexer_client = SearchIndexerClient(endpoint, credential)
        
#         # Document Intelligence 的 Web API 技能
#         document_intelligence_skill = WebApiSkill(
#             name="document-intelligence-layout",
#             description="使用Document Intelligence分析文档布局和结构",
#             context="/document",
#             uri=di_endpoint.rstrip('/') + "/formrecognizer/documentModels/prebuilt-layout:analyze?api-version=2023-07-31",
#             http_method="POST",
#             timeout="PT230S",  # 3分50秒超时
#             batch_size=1,
#             degree_of_parallelism=1,
#             inputs=[
#                 InputFieldMappingEntry(name="file", source="/document/$value"),  # 原始文件数据
#             ],
#             outputs=[
#                 OutputFieldMappingEntry(name="content", target_name="di_content"),  # 提取的文本内容
#                 OutputFieldMappingEntry(name="pages", target_name="di_pages"),      # 页面信息
#                 OutputFieldMappingEntry(name="tables", target_name="di_tables"),    # 表格数据
#                 OutputFieldMappingEntry(name="sections", target_name="di_sections"), # 文档章节
#                 OutputFieldMappingEntry(name="paragraphs", target_name="di_paragraphs") # 段落信息
#             ],
#             http_headers={
#                 "Ocp-Apim-Subscription-Key": di_key
#             }
#         )
        
#         # 智能分块技能 - 基于语义的分块
#         split_skill = SplitSkill(
#             name="semantic-chunking",
#             description="基于语义的智能文本分块，适合RAG",
#             context="/document/di_pages/*",
#             text_split_mode="pages",
#             maximum_page_length=500,  # 每个块约500字符，适合RAG
#             page_overlap_length=50,   # 块之间重叠50字符，保持上下文
#             inputs=[
#                 InputFieldMappingEntry(name="text", source="/document/di_content")
#             ],
#             outputs=[
#                 OutputFieldMappingEntry(name="textItems", target_name="chunks")
#             ]
#         )
        
#         # 创建技能集
#         skillset = SearchIndexerSkillset(
#             name="di-layout-chunking-skillset",
#             description="使用Document Intelligence Layout和智能分块的技能集",
#             skills=[document_intelligence_skill, split_skill]
#         )
        
#         # 创建技能集
#         result = indexer_client.create_skillset(skillset)
        
#         return func.HttpResponse(
#             "✅ Document Intelligence Skillset 创建成功！\n"
#             "包含：\n"
#             "• Document Intelligence Layout - 精确的文档结构分析\n"  
#             "• 智能语义分块 - 适合RAG的文本分块",
#             status_code=200
#         )
        
#     except Exception as e:
#         return func.HttpResponse(f"创建Skillset错误: {str(e)}", status_code=500)
    


@app.route(route="upload_to_blob", methods=["GET", "POST"])
def upload_to_blob(req: func.HttpRequest) -> func.HttpResponse:
    # file_path = "travelguide_epos_platinum_SompoJapan.pdf"
    # blob_url = upload_file_to_blob(file_path)

    file_path = "travelguide_epos_platinum_SompoJapan.pdf"
    file_name = os.path.basename(file_path)
    blob_url = upload_file_to_blob(file_path, file_name)

    return func.HttpResponse(
        f"✅ 文件上传成功！\nBlob URL: {blob_url}",
        status_code=200
    )
 
@app.route(route="create_index", auth_level=func.AuthLevel.FUNCTION)
def create_index(req: func.HttpRequest) -> func.HttpResponse:
    try:
        search_service_name = os.environ["SEARCH_SERVICE_NAME"]
        admin_key = os.environ["SEARCH_ADMIN_KEY"]
        endpoint = f"https://{search_service_name}.search.windows.net"
        
        credential = AzureKeyCredential(admin_key)
        search_index_client = SearchIndexClient(endpoint, credential)
        
        # 修复字段定义
        fields = [
            SimpleField(name="id", type="Edm.String", key=True, filterable=True),
            SearchableField(name="content", type="Edm.String", searchable=True, analyzer="zh-Hans.microsoft"),
            SimpleField(name="file_name", type="Edm.String", filterable=True),
            SimpleField(name="title", type="Edm.String", filterable=True),
            SimpleField(name="chunk_id", type="Edm.String", filterable=True),
            SimpleField(name="page_number", type="Edm.Int32", filterable=True, sortable=True),
        ]
        
        index_name = req.params.get('index_name', 'pdf-documents')
        index = SearchIndex(name=index_name, fields=fields)
        result = search_index_client.create_index(index)
        
        return func.HttpResponse(f"✅ 索引 '{index_name}' 创建成功！", status_code=200)
        
    except Exception as e:
        return func.HttpResponse(f"创建索引错误: {str(e)}", status_code=500)
    

@app.route(route="create_simple_skillset", auth_level=func.AuthLevel.FUNCTION)
def create_simple_skillset(req: func.HttpRequest) -> func.HttpResponse:
    """创建包含基础技能的最小技能集"""
    try:
        search_service_name = os.environ["SEARCH_SERVICE_NAME"]
        admin_key = os.environ["SEARCH_ADMIN_KEY"]
        endpoint = f"https://{search_service_name}.search.windows.net"
        
        credential = AzureKeyCredential(admin_key)
        indexer_client = SearchIndexerClient(endpoint, credential)
        
        # 创建一个简单的文本处理技能
        from azure.search.documents.indexes.models import TextTranslationSkill, TextSplitMode
        
        # 使用最简单的技能 - 文本翻译（即使不翻译也可以）
        translation_skill = TextTranslationSkill(
            name="basic-text-skill",
            description="基础文本处理技能",
            context="/document",
            inputs=[
                InputFieldMappingEntry(name="text", source="/document/content")
            ],
            outputs=[
                OutputFieldMappingEntry(name="translatedText", target_name="processed_content")
            ],
            default_to_language_code="zh-Hans"
        )
        
        skillset = SearchIndexerSkillset(
            name="pdf-basic-skillset",
            description="基础PDF处理技能集",
            skills=[translation_skill]  # 至少包含一个技能
        )
        
        result = indexer_client.create_skillset(skillset)
        return func.HttpResponse("✅ 基础技能集创建成功！", status_code=200)
        
    except Exception as e:
        return func.HttpResponse(f"创建技能集错误: {str(e)}", status_code=500)

@app.route(route="create_basic_indexer", auth_level=func.AuthLevel.FUNCTION)
def create_basic_indexer(req: func.HttpRequest) -> func.HttpResponse:
    """创建基础索引器 - 不使用技能集"""
    try:
        search_service_name = os.environ["SEARCH_SERVICE_NAME"]
        admin_key = os.environ["SEARCH_ADMIN_KEY"]
        endpoint = f"https://{search_service_name}.search.windows.net"
        
        credential = AzureKeyCredential(admin_key)
        indexer_client = SearchIndexerClient(endpoint, credential)
        
        # 简化参数 - 禁用图片处理避免额外费用
        parameters = IndexingParameters(configuration={
            "dataToExtract": "contentAndMetadata",
            "imageAction": "none",  # 禁用图片处理
            "parsingMode": "default"
        })
        
        # 基础索引器 - 不使用技能集
        indexer = SearchIndexer(
            name="pdf-basic-indexer",
            data_source_name="azureblob-1760554125253-datasource",
            target_index_name="pdf-documents",
            parameters=parameters,
            field_mappings=[
                FieldMapping(source_field_name="metadata_storage_name", target_field_name="file_name"),
                FieldMapping(source_field_name="metadata_storage_path", target_field_name="title"),
                # 使用 metadata_storage_content_type 或其他可用字段作为 chunk_id
                FieldMapping(source_field_name="metadata_storage_content_type", target_field_name="chunk_id"),
            ]
        )
        
        result = indexer_client.create_indexer(indexer)
        return func.HttpResponse("✅ 基础索引器创建成功！", status_code=200)
        
    except Exception as e:
        return func.HttpResponse(f"创建索引器错误: {str(e)}", status_code=500)
    
@app.route(route="run_basic_indexer", auth_level=func.AuthLevel.FUNCTION)
def run_basic_indexer(req: func.HttpRequest) -> func.HttpResponse:
    """运行基础索引器"""
    try:
        search_service_name = os.environ["SEARCH_SERVICE_NAME"]
        admin_key = os.environ["SEARCH_ADMIN_KEY"]
        endpoint = f"https://{search_service_name}.search.windows.net"
        
        credential = AzureKeyCredential(admin_key)
        indexer_client = SearchIndexerClient(endpoint, credential)
        
        indexer_client.run_indexer("pdf-basic-indexer")
        return func.HttpResponse("✅ 基础索引器已启动！正在处理PDF文件...", status_code=200)
        
    except Exception as e:
        return func.HttpResponse(f"运行索引器错误: {str(e)}", status_code=500)
    
@app.route(route="check_indexer_status", auth_level=func.AuthLevel.FUNCTION)
def check_indexer_status(req: func.HttpRequest) -> func.HttpResponse:
    """详细检查索引器状态"""
    try:
        search_service_name = os.environ["SEARCH_SERVICE_NAME"]
        admin_key = os.environ["SEARCH_ADMIN_KEY"]
        endpoint = f"https://{search_service_name}.search.windows.net"
        
        credential = AzureKeyCredential(admin_key)
        indexer_client = SearchIndexerClient(endpoint, credential)
        
        # 获取索引器状态
        status = indexer_client.get_indexer_status("pdf-basic-indexer")
        
        status_info = {
            "indexer_name": "pdf-basic-indexer",
            "overall_status": status.status,
            "last_run_status": status.last_result.status if status.last_result else "N/A",
            "last_run_error": status.last_result.error_message if status.last_result and status.last_result.error_message else "No errors",
            "items_processed": status.last_result.item_count if status.last_result else 0,
            "failed_items": status.last_result.failed_item_count if status.last_result else 0,
            "start_time": status.last_result.start_time.isoformat() if status.last_result and status.last_result.start_time else "N/A",
            "end_time": status.last_result.end_time.isoformat() if status.last_result and status.last_result.end_time else "N/A",
            "execution_history_available": status.execution_history is not None
        }
        
        import json
        return func.HttpResponse(
            json.dumps(status_info, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        return func.HttpResponse(f"检查状态错误: {str(e)}", status_code=500)
    
@app.route(route="check_blob_files", auth_level=func.AuthLevel.FUNCTION)
def check_blob_files(req: func.HttpRequest) -> func.HttpResponse:
    """检查Blob容器中的文件"""
    from azure.storage.blob import BlobServiceClient
    import json
    
    try:
        connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = os.environ["BLOB_CONTAINER_NAME"]
        
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        
        # 列出所有blob文件
        blob_list = list(container_client.list_blobs())
        
        file_info = []
        for blob in blob_list:
            file_info.append({
                "name": blob.name,
                "size": blob.size,
                "last_modified": blob.last_modified.isoformat() if blob.last_modified else "N/A"
            })
        
        return func.HttpResponse(
            json.dumps({
                "container": container_name,
                "file_count": len(blob_list),
                "files": file_info
            }, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        return func.HttpResponse(f"检查Blob文件错误: {str(e)}", status_code=500)
    

@app.route(route="check_index_docs", auth_level=func.AuthLevel.FUNCTION)
def check_index_docs(req: func.HttpRequest) -> func.HttpResponse:
    """检查索引中的文档"""
    from azure.search.documents import SearchClient
    import json
    
    try:
        search_service_name = os.environ["SEARCH_SERVICE_NAME"]
        admin_key = os.environ["SEARCH_ADMIN_KEY"]
        endpoint = f"https://{search_service_name}.search.windows.net"
        
        credential = AzureKeyCredential(admin_key)
        search_client = SearchClient(endpoint, "pdf-documents", credential)
        
        # 获取文档数量
        doc_count = search_client.get_document_count()
        
        # 尝试搜索文档
        results = list(search_client.search(
            search_text="*",
            select="id,file_name,title",
            top=10
        ))
        
        return func.HttpResponse(
            json.dumps({
                "index_name": "pdf-documents",
                "total_documents": doc_count,
                "search_results_count": len(results),
                "sample_documents": [
                    {"id": doc["id"], "file_name": doc.get("file_name"), "title": doc.get("title")} 
                    for doc in results
                ]
            }, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        return func.HttpResponse(f"检查索引文档错误: {str(e)}", status_code=500)