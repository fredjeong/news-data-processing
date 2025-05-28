"""
Elasticsearch 관련 유틸리티 함수들을 모아놓은 모듈입니다.
news_articles 인덱스에 뉴스 기사를 저장하는 기능을 제공합니다.
"""

import json
from elasticsearch import Elasticsearch
import sys
from os import path

root_dir = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(root_dir)

from config import ES_CONFIG

index_name = ES_CONFIG['index']

def get_elasticsearch_client():
    """Elasticsearch 클라이언트를 반환합니다."""
    try:
        es = Elasticsearch(
            f"http://{ES_CONFIG['host']}:{ES_CONFIG['port']}",
            basic_auth=(ES_CONFIG['user'], ES_CONFIG['password'])
        )
        return es
    except Exception as e:
        print(f"Elasticsearch 연결 실패: {e}")
        return None

def create_index_if_not_exists(es):
    
    """news_articles 인덱스가 없으면 생성합니다."""
    if not es.indices.exists(index=index_name, ignore=400):
        # 인덱스 설정 (한국어 검색을 위한 nori 분석기 사용)
        
        body = {
            "settings": {
                "analysis": {
                    "tokenizer": {
                        "nori_tokenizer_with_options": {
                            "type": "nori_tokenizer",
                            "decompound_mode": "mixed",
                            # "discard_punctuation": "true"
                        }
                    },
                    "filter": {
                        "korean_stop": {
                            "type": "stop",
                            "stopwords": [
                                "은", "는", "이", "가", "을", "를", "의", "에", "에서", "로", "으로", 
                                "와", "과", "도", "만", "부터", "까지", "이나", "나", "이라", "라", "이며", 
                                "며", "이고", "고", "든지", "이든지", "거나", "이거나", "하고", "이야", "야"
                            ]
                        }
                    },
                    "analyzer": {
                        "korean": {
                            "type": "custom",
                            "tokenizer": "nori_tokenizer_with_options",
                            "filter": ["lowercase", "korean_stop"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "company": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "korean"},
                    "content": {"type": "text", "analyzer": "korean"},
                    "summary": {"type": "text", "analyzer": "korean"},
                    "keywords": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "writer": {"type": "keyword"},
                    "write_date": {
                        "type": "date", 
                        "format": "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss.SSSZ||yyyy-MM-dd'T'HH:mm:ssXXX||strict_date_optional_time||epoch_millis"
                    },
                    "url": {"type": "keyword"}
                }
            }
        }
    
        es.indices.create(index=index_name, body=body)

def send_to_elasticsearch(data, article_id):
    """PostgreSQL에 저장된 뉴스 기사를 Elasticsearch에 저장합니다."""
    
    es = get_elasticsearch_client()
    if not es:
        print("Elasticsearch 클라이언트 생성 실패")
        return False
    
    create_index_if_not_exists(es)
    
    
    # 날짜 형식 전처리
    write_date = data["write_date"]
    # ISO 8601 형식을 Elasticsearch에서 인식할 수 있는 형식으로 변환
    try:
        # 날짜 형식이 ISO 8601(예: 2025-05-16T13:56:00+09:00)인 경우, 시간 부분을 제거
        if "T" in write_date:
            write_date = write_date.split("T")[0]
        else:
            write_date = write_date.split()[0]
    except Exception as e:
        print(f"날짜 형식 처리 중 오류: {e}")
        # 오류 발생 시 기본값 설정
        write_date = "2000-01-01"
    
    # 데이터 준비
    doc = {
        "company": data["company"],
        "title": data["title"],
        "content": data["content"],
        "summary": data["summary"],
        "keywords": json.loads(data["keywords"]) if isinstance(data["keywords"], str) else data["keywords"],
        # "keywords": data["keywords"],
        "category": data["category"],
        "writer": data["writer"],
        "write_date": write_date,
        "url": data["url"],
        "postgresql_id": article_id
    }
    
    try:
        # Elasticsearch에 문서 색인
        res = es.index(index=index_name, id=article_id, body=doc)
        print(f"Elasticsearch에 문서 저장 완료 (ID: {article_id}): {res['result']}")
        return True
    except Exception as e:
        print(f"Elasticsearch 데이터 저장 실패: {e}")
        return False 