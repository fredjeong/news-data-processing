# 뉴스 데이터 파이프라인 구축 프로젝트

### 프로젝트 구조

```
.
├── __init__.py
├── architecture.txt
├── config.py
├── extract
│   ├── kafka_producer.py
│   ├── main.py
│   ├── rss_reader.py
│   └── selenium_crawler.py
├── flink-sql-connector-kafka-3.3.0-1.20.jar
├── install-guide
│   ├── docker-install.md
│   ├── flink-install.md
│   ├── java-install.md
│   ├── kafka-install.md
│   ├── ollama-install.md
│   ├── postgresql-install.md
│   └── spark-install.md
├── README.md
├── requirements.txt
└── transform-and-load
    ├── flink.py
    ├── utils_pipeline.py
    └── utils_preprocessing.py

4 directories, 20 files
 ```

### 0. 최종 목표

```
  [Extract]                    [Transform]            [Load]
 Kafka Topic   →    Flink   →  데이터 처리/변환   →  PostgreSQL(DB 저장)
(JSON or RSS)      (스트리밍)    (카테고리 분류)    →  Elasticsearch(검색)
                      │        (키워드 추출)      
                      │        (벡터 임베딩)
                      │
                      ↓            
                     HDFS  →  Spark  →  리포트 생성  →  HDFS 아카이브
                   (임시저장)   (배치)       (pdf)       (장기 보관)
```

- 이후 상기 과정 AirFlow 이용하여 자동화

### 1. 환경 설정

- [Docker](./install-guide/docker-install.md)
- [Java](./install-guide/java-install.md)
- [Kafka](./install-guide/kafka-install.md)
- [Flink](./install-guide/flink-install.md)
- [Spark](./install-guide/spark-install.md)
- [PostgreSQL](./install-guide/postgresql-install.md)

### 2. RSS 토픽과 연결

#### 목표

- RSS 피드를 주기적으로 파싱하고 해당 내용을 Kafka 토픽으로 전송하는 Producer를 구현
  - RSS 피드에서 최신 뉴스 항목 수집
  - 뉴스 본문을 크롤링하여 Kafka 토픽으로 전송
  - JSON 형식으로 Kafka에 직렬화하여 전송 

#### 단계

1. Zookeeper 및 Kafka 실행

2. Kafka 토픽 생성 (news-articles)

```bash
$KAFKA_HOME/bin/kafka-topics.sh --create --topic news-articles --partitions 8 --bootstrap-server localhost:9092
```

- 파티션을 8개로 설정하여 병렬 처리

3. Kafka Producer 실행

```bash
python3 ./extract/main.py
```

### 3. Flink 기반 실시간 뉴스 처리

#### 목표

- Kafka로부터 전송된 뉴스 데이터를 Flink에서 소비(consume)하고, 이를 전처리하여 PostgreSQL에 저장하는 실시간 데이터 처리 환경 구성

#### 단계

1. Kafka에서 메시지 수신 (`FlinkKafkaConsumer`)
2. 수신된 뉴스 본문(`content`)을 기반으로 전처리 수행
  - 키워드 추출: 본문에서 핵심 키워드 5개 추출
  - 벡터 임베딩: OpenAI Embedding API를 이용해 1536차원 벡터 생성
  - 카테고리 추론: Zero-shot Learning 방식으로 뉴스 주제를 자동 분류
3. 전처리된 결과를 PostgreSQL에 저장

