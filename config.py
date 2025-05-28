from dotenv import load_dotenv
import os

load_dotenv()

# .env 파일로 관리
USERID = os.environ.get('POSTGRESQL_USERNAME')
PASSWORD = os.environ.get('POSTGRESQL_PASSWORD')

KAFKA_TOPIC_NAME = "news-articles"
DB_NAME = "news"
TABLE_NAME = "news_articles"
EMBEDDING_MODEL = "nlpai-lab/KURE-v1" # 한국어 임베딩 특화
EMBEDDING_DIM = 1024
LLM_MODEL = "exaone3.5:2.4b"
HOST = "localhost"
POSTGRESQL_PORT = 5432
KAFKA_PORT = 9092
ELASTICSEARCH_PORT = 9200

# 언론사, RSS피드 주소
RSS_FEEDS = {
    # "조선일보": "https://www.chosun.com/arc/outboundfeeds/rss/category/economy/?outputType=xml",
    "경향신문": "https://www.khan.co.kr/rss/rssdata/economy_news.xml",
    # "연합뉴스": "https://www.yna.co.kr/rss/economy.xml",
    # '매일경제': 'https://www.mk.co.kr/rss/30100041/'
}

# PostgreSQL 서버 접속 정보
DB_CONFIG = {
    "dbname": DB_NAME,
    "tablename": TABLE_NAME,
    "user": USERID,
    "password": PASSWORD,
    "host": HOST,
    "port": POSTGRESQL_PORT
}

# Kafka 접속 정보
KAFKA_CONFIG = {
    "bootstrap_servers": f"{HOST}:{KAFKA_PORT}",
    "topic": KAFKA_TOPIC_NAME,
}

# 임베딩, LLLM 모델
MODELS_CONFIG = {
    "embedding_model": EMBEDDING_MODEL,
    "embedding_dim": EMBEDDING_DIM,
    "llm_model": LLM_MODEL
}

# Elasticsearch 접속 정보
ES_CONFIG = {
    "host": HOST,
    "port": ELASTICSEARCH_PORT,
    "index": "news_articles",
    "user": "elastic",
    "password": "elastic123",
    "use_ssl": False
}