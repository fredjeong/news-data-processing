# Data Pipeline

## 전체 구조와 목적

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

뉴스 기사를 다양한 소스로부터 수집하여, 실시간으로 전처리 및 분석 후, 검색 및 추천이 가능한 형태로 저장합니다. 데이터의 신뢰성과 확장성을 위해 메시지 큐(Kafka), 스트림 처리(Flink), 관계형 데이터베이스(PostgreSQL), 검색 엔진(Elasticsearch) 등 다양한 기술을 조합합니다.

## 주요 기술과 설계 의도

### 1. Kafka: 데이터 수집의 비동기화와 확장성

뉴스 데이터는 다양한 소스에서 비동기적으로 유입됩니다. Kafka를 도입함으로써 데이터 생산(수집)과 소비(처리)를 분리하여, 시스템 확장성과 장애 내성을 확보할 수 있습니다. `main_kafka.py` 파일은 신문사들의 RSS 피드를 이용하여 크롤링한 기사를 Kafka 토픽에 전송하고, `main_kafka_csv.py` 파일은 csv 형태로 저장되어 있는 기사 데이터를 Kafka 토픽에 전송합니다. 각 기사는 JSON 형태로 Kafka에 적재되어, 이후 실시간 처리 시스템이 이를 구독할 수 있습니다.

- Zookeeper 및 Kafka 서버 실행
- Kafka 토픽 생성 (파티션 8개로 병렬 처리)
    ```bash
    $KAFKA_HOME/bin/kafka-topics.sh --create --topic news-articles --partitions 8 --bootstrap-server localhost:9092
    ```
- 메인 파일 실행
    ```bash
    python3 ./main/main_kafka.py # 신문사 RSS 피드를 이용하여 데이터 수집
    python3 ./main/main_kafka_csv.py # csv 파일 로드하여 사용
    ```

### 2. Flink: 실시간 데이터 처리와 파이프라인 자동화

실시간으로 유입되는 대량의 뉴스 데이터를 빠르게 전처리하고, 다양한 분석(카테고리 분류, 키워드 추출, 임베딩 등)을 수행하기 위해 Flink를 사용합니다. `main_flink.py` 파일은 Kafka 토픽으로부터 메시지를 받아, 데이터 전처리 및 분석을 수행합니다. 

가장 먼저 정규표현식을 사용해 기사의 내용 중 `\t`, `\n`과 같은 이스케이프 시퀀스를 제거합니다. 다음으로 LLM을 이용하여 기사의 핵심 내용을 담은 요약본을 생성하고 키워드 다섯 개를 추출, 카테고리를 분류하는 작업을 수행하며, 이어서 이후 유사도 기반 추천 및 분류 작업에 사용될 수 있도록 기사의 의미를 임베딩한 벡터를 생성합니다. 언어 모델로는 LG AI Research의 오픈소스 모델인 [`Exaone 3.5:2.4b`](https://github.com/LG-AI-EXAONE/EXAONE-3.5)가 사용되었으며, 임베딩 모델로는 마이크로소프트에서 개발한 [`multilingual-e5-large-instruct`](https://arxiv.org/pdf/2402.05672) 모델이 사용되었습니다.

이러한 처리 과정을 거친 데이터는 PostgreSQL 데이터베이스와 HDFS에 저장됩니다. 데이터베이스에 추가적으로 저장된 기사들은 Elasticsearch에 색인되어 추후 제목, 본문, 요약, 키워드 등 다양한 필드 기반의 검색을 가능하게 합니다. 기사의 URL을 기준으로 중복을 파악하여 동일한 기사가 데이터베이스에 존재할 시 처리를 건너뛰고, 저장이 실패했을 경우 트랜잭션을 롤백하여 데이터 일관성을 유지합니다.

```bash
python3 ./main/main_flink.py
```

> 참고:  
> 설치 및 환경 설정 등과 관련한 내용은 [상위 README 파일](../README.md)을 참고하세요.