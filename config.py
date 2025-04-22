from dotenv import load_dotenv
import os

load_dotenv()

USERID = os.environ.get('POSTGRESQL_USERID')
PASSWORD = os.environ.get('POSTGRESQL_PASSWORD')

# 언론사, RSS피드 주소
RSS_FEEDS = {
    # "조선일보": "https://www.chosun.com/arc/outboundfeeds/rss/category/economy/?outputType=xml",
    "경향신문": "https://www.khan.co.kr/rss/rssdata/economy_news.xml",
    # "연합뉴스": "https://www.yna.co.kr/rss/economy.xml",
    # '매일경제': 'https://www.mk.co.kr/rss/30100041/'
}

# PostgreSQL 서버 접속 정보
DB_CONFIG = {
    "dbname": "news",
    "user": USERID,
    "password": PASSWORD,
    "host": "localhost",
    "port": 5432
}

# Kafka 접속 정보
KAFKA_CONFIG = {
    "bootstrap_servers": "localhost:9092",
    "topic": "news-articles"
}
