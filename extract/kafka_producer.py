from kafka import KafkaProducer
import json
from selenium_crawler import get_content_from_link
# from config import KAFKA_CONFIG

# Kafka 프로듀서 설정
producer = KafkaProducer(
    # bootstrap_servers=KAFKA_CONFIG["bootstrap_servers"],
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)


# 기사 1건 처리 및 Kafka 전송
def process_and_send(journal: str, entry: dict):
    try:
        write_date = entry.get('published', '') if journal != '경향신문' else entry.get('updated', '')
        content = get_content_from_link(entry['link'])

        article_data = {
            "title": entry.get("title"),
            "writer": entry.get("author", ""),
            "write_date": write_date,
            "content": content,
            "url": entry.get("link"),
        }

        # Kafka로 전송
        try:
            producer.send('news-articles', article_data)
            print(f"[Kafka 전송 성공] {article_data.get('title')}")
        except Exception as e:
            print(f"[Kafka 전송 실패] {e}")

    except Exception as e:
        print(f"[오류] {journal} 기사 처리 중 실패: {e}")
