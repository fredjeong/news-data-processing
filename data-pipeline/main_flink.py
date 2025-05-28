"""
FLINK 기반 뉴스 처리

Kafka 토픽(news)으로 들어온 뉴스 메시지를 Flink가 수신하여 처리하고, 
해당 결과를 PostgreSQL의 news_articles 테이블에 적재합니다.
PostgreSQL에 정상적으로 적재된 데이터만 Elasticsearch와 JSON 파일로 저장됩니다.

[핵심 흐름]
1. Kafka에서 메시지 수신 (FlinkKafkaConsumer)
2. 수신된 뉴스 본문(content)을 기반으로 전처리 수행
3. 카테고리 추론: transform_classify_category
4. 키워드 추출: transform_extract_keywords
5. 벡터 임베딩: transform_to_embedding
6. 트랜잭션 처리:
   - PostgreSQL에 저장 (INSERT INTO news_articles)
   - 성공 시 JSON 파일로 저장 및 Elasticsearch에 색인
   - 실패 시 트랜잭션 롤백
"""

"""
본문이 없는 기사는?
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
# from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.datastream.connectors.kafka import KafkaOffsetsInitializer
from pyflink.common.watermark_strategy import WatermarkStrategy

import json

import sys
from os import path

root_dir = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(root_dir)

from config import KAFKA_CONFIG

utils_dir = path.join(root_dir, 'data-pipeline/utils')
sys.path.append(utils_dir)

import utils_pipeline 


def run():
    # 실행환경 설정
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(8)


    # Kafka connector JAR 등록
    dir_path = path.dirname(path.dirname(path.abspath(__file__)))
    kafka_connector_path = f"{dir_path}/flink-sql-connector-kafka-3.3.0-1.20.jar"
    env.add_jars(f"file://{kafka_connector_path}")

    # Kafka Consumer 설정
    kafka_props = {
        'bootstrap.servers': KAFKA_CONFIG['bootstrap_servers'],
        'group.id': 'flink_consumer_group'
    }

    consumer = KafkaSource.builder() \
        .set_bootstrap_servers(KAFKA_CONFIG['bootstrap_servers']) \
        .set_topics(KAFKA_CONFIG['topic']) \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    # Kafka에서 메시지 수신
    stream = env.from_source(consumer, WatermarkStrategy.no_watermarks(), KAFKA_CONFIG['topic'])

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

    env.execute("Flink Kafka Consumer Job with PostgreSQL and Elasticsearch Sink")

    consumer.close()

if __name__ == "__main__":
    run()