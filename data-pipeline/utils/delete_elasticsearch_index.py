from elasticsearch import Elasticsearch
from config import ES_CONFIG

if __name__ == "__main__":
    es = Elasticsearch(
        [f"http://{ES_CONFIG['host']}:{ES_CONFIG['port']}"],
        basic_auth=(ES_CONFIG['user'], ES_CONFIG['password']),
        verify_certs=ES_CONFIG['use_ssl']
    )
    if es.indices.exists(index="news_articles", ignore=[400, 404]):
        es.indices.delete(index="news_articles", ignore=[400, 404])
        print("news_articles 인덱스 삭제 완료")
    else:
        print("news_articles 인덱스가 존재하지 않습니다.")