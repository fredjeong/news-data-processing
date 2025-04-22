"""
FLINK 기반 뉴스 처리

Kafka 토픽(news)으로 들어온 뉴스 메시지를 Flink가 수신하여 처리하고, 
해당 결과를 PostgreSQL의 news_articles 테이블에 적재합니다.

[핵심 흐름]
1. Kafka에서 메시지 수신 (FlinkKafkaConsumer)
2. 수신된 뉴스 본문(content)을 기반으로 전처리 수행
3. 카테고리 추론: transform_classify_category
4. 키워드 추출: transform_extract_keywords
5. 벡터 임베딩: transform_to_embedding
6. 전처리된 결과를 PostgreSQL에 저장 (INSERT INTO news_articles)
"""

"""
본문이 없는 기사는?
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
# from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.datastream.connectors.kafka import KafkaOffsetsInitializer
from pyflink.datastream.connectors.jdbc import JdbcSink, JdbcExecutionOptions, JdbcConnectionOptions
from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import WatermarkStrategy

import os
from dotenv import load_dotenv
import psycopg2
import datetime

import json
import utils_pipeline

from sys import path

load_dotenv()

API_KEY = os.environ.get('OPENAI_API_KEY')
USERID = os.environ.get('POSTGRESQL_USERID')
PASSWORD = os.environ.get('POSTGRESQL_PASSWORD')

# PostgreSQL 데이터베이스 연결 설정
conn = psycopg2.connect(
    dbname='news',  # 데이터베이스 이름
    user=USERID,  # 사용자 이름
    password=PASSWORD,  # 비밀번호
    host='localhost',  # 호스트 주소 (여기서는 로컬 호스트)
    port=5432  # 포트 번호
)
cursor = conn.cursor()  # 데이터베이스와 상호 작용하기 위한 커서 객체 생성

# 실행환경 설정
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(8)




# Kafka connector JAR 등록
# parent_dir = path.dirname(path.dirname(path.abspath(__file__)))
# kafka_connector_path = f"{parent_dir}/flink-sql-connector-kafka-3.3.0-1.20.jar"
kafka_connector_path = "/Users/fredjeong/Desktop/news/flink-sql-connector-kafka-3.3.0-1.20.jar"
env.add_jars(f"file://{kafka_connector_path}")

# Kafka Consumer 설정
kafka_props = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'flink_consumer_group'
}

consumer = KafkaSource.builder() \
    .set_bootstrap_servers('localhost:9092') \
    .set_topics("news-articles") \
    .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

# Kafka에서 메시지 수신
stream = env.from_source(consumer, WatermarkStrategy.no_watermarks(), "news-articles")

def find_location(data):
    data_ = json.loads(data)
    if not data_['content']:
        string = "빈"
    else:
        string = "내용 있는"
    print(f"새로운 {string} 기사 처리 중")
    return data

# 전처리 및 저장 파이프라인 구성
processed_stream = stream.map(find_location).map(utils_pipeline.preprocess).map(utils_pipeline.add_to_db) 

env.execute("Flink Kafka Consumer Job with PostgreSQL Sink")

consumer.close()
