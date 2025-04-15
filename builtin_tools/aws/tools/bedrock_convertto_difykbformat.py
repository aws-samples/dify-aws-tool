import json
import os
import uuid
from datetime import datetime

class LambdaConverttoDifykbformat:

    def remove_before_single_slash(s):
        s=s.replace("s3://","")
        parts = s.split('/')
        if parts:
            result = parts[-1]
        else:
            result = s
        return result

    # 将bedrock retrieve格式取回的json转化为dify知识库返回格式
    # bedrock 返回json格式为：
    # {
    # "text": "",
    # "files": [],
    # "json": [
    #     {
    #     "results": [
    #         {
    #         "content": "# 将S3到EC2的数据传输推向极限.",
    #         "metadata": {
    #             "x-amz-bedrock-kb-chunk-id": "1%3A0%3AqDlyE5YBpxO2MuL4JdPm",
    #             "x-amz-bedrock-kb-data-source-id": "TKW1WS77RH",
    #             "x-amz-bedrock-kb-document-page-number": 0,
    #             "x-amz-bedrock-kb-source-uri": "s3://mmu-workshop-509399592849/mm-data/S3.pdf"
    #         },
    #         "score": 0.3708723
    #         }
    #     ]}]
    #     }
    def convertto_dify_kbformat(input_json) :
        result_array = []
        kb_result =""
        index = 1
        for idx, item in enumerate(input_json[0]['results']):
            # 提取基础字段
            source_uri = item['metadata']['x-amz-bedrock-kb-source-uri']
            page_number = item['metadata'].get('x-amz-bedrock-kb-document-page-number', 0)
            data_source_id = item['metadata'].get('x-amz-bedrock-kb-data-source-id', 'NextCloud')
            score = item.get('score', 0.0)
            
            # 生成动态字段
            document_name = remove_before_single_slash(source_uri)  # 去除扩展名
            
            # 构建元数据
            metadata = {
                "_source": "knowledge",
                "dataset_id": "",
                "dataset_name": "BedRock知识库",
                "document_id": str(uuid.uuid4()),
                "document_name": document_name,
                "document_data_source_type": data_source_id,
                "segment_id": str(uuid.uuid4()),
                "retriever_from": "workflow",
                "score": round(score, 6),
                "segment_hit_count": page_number,  # 示例值递增
                "segment_word_count": len(item['content'].split()),  # 计算词数
                "segment_position": page_number,
                "doc_metadata": {
                    "tag": "nextcloud",
                    "source": "file_upload",
                    "uploader": "advantage",
                    "upload_date": int(datetime(2024, 5, 10).timestamp()),  # 固定时间戳
                    "document_name": document_name,
                    "last_update_date": int(datetime(2024, 5, 10).timestamp())
                },
                "position": idx + 1
            }
            if item['content'].strip() != "" :
                result_array.append({
                    "content": item['content'],
                    "title": f"{document_name}",  # 添加默认扩展名
                    "metadata": metadata
                })
                content = item.get("content")
                kb_result += f"{index}.{content}\n"
                index += 1
        return result_array