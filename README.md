# 뉴스 데이터 파이프라인 구축 프로젝트

- [뉴스 데이터 파이프라인 구축 프로젝트](#뉴스-데이터-파이프라인-구축-프로젝트)
  * [1. 프로젝트 전체 구조](#1-프로젝트-전체-구조)
  * [2. Data Engineering](#2-data-engineering)
    + [2.1 구조](#22-최종-목표)
    + [2.2 최종 목표](#22-최종-목표)
    + [2.3 환경 설정](#23-환경-설정)
    + [2.4 RSS 토픽과 연결](#24-rss-토픽과-연결)
      - [2.4.1 목표](#241-목표)
      - [2.4.2 단계](#242-단계)
    + [2.5 Flink 기반 실시간 뉴스 처리](#25-flink-기반-실시간-뉴스-처리)
      - [2.5.1 사전 작업](#251-사전-작업)
      - [2.5.2 목표](#252-목표)
      - [2.5.3 실행](#253-실행)
  * [3. Backend](#3-backend)
    + [3.1 구조](#31-구조)
    + [3.2 News Articles](#32-news-articles)
    + [3.3 Accounts](#33-accounts)
  * [4. AI](#4-ai)
    + [4.1 기사 추천 시스템](#41-기사-추천-시스템)
    + [4.2 챗봇 기반 기사 찾기](#42-챗봇-기반-기사-찾기)
    + [4.3 RAG](#43-rag)

## 1. 프로젝트 전체 구조

```
.
├── README.md
├── __init__.py
├── architecture.txt
├── backend
├── config.py
├── data-engineering
├── flink-sql-connector-kafka-3.3.0-1.20.jar
├── install-guide
└── requirements.txt
 ```

## 2. Data Engineering

### 2.1 구조

```
.
├── extract
│   ├── kafka_producer.py
│   ├── main.py
│   ├── rss_reader.py
│   └── selenium_crawler.py
└── transform-and-load
    ├── flink.py
    ├── utils_pipeline.py
    └── utils_preprocessing.py
```

### 2.2 최종 목표

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

### 2.3 환경 설정

- [Docker](./install-guide/docker-install.md)
- [Java](./install-guide/java-install.md)
- [Kafka](./install-guide/kafka-install.md)
- [Flink](./install-guide/flink-install.md)
- [Spark](./install-guide/spark-install.md)
- [PostgreSQL](./install-guide/postgresql-install.md)
- [Ollama](./install-guide/ollama-install.md)
- [Django](./install-guide/django-install.md)

### 2.4 RSS 토픽과 연결

#### 2.4.1 목표

- RSS 피드를 주기적으로 파싱하고 해당 내용을 Kafka 토픽으로 전송하는 Producer를 구현
  - RSS 피드에서 최신 뉴스 항목 수집
  - 뉴스 본문을 크롤링하여 Kafka 토픽으로 전송
  - JSON 형식으로 Kafka에 직렬화하여 전송 

#### 2.4.2 단계

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

### 2.5 Flink 기반 실시간 뉴스 처리

#### 2.5.1 사전 작업

- 디렉토리 최상단에 .env 파일 만들어서 PostgreSQL의 `USERNAME`과 `PASSWORD` 정의

#### 2.5.2 목표

- Kafka로부터 전송된 뉴스 데이터를 Flink에서 소비(consume)하고, 이를 전처리하여 PostgreSQL에 저장하는 실시간 데이터 처리 환경 구성

  1. Kafka에서 메시지 수신 (`FlinkKafkaConsumer`)
  2. 수신된 뉴스 본문(`content`)을 기반으로 전처리 수행
    - 키워드 추출: 오픈소스 모델 `exaone3.5:2.4b`를 이용해 본문에서 핵심 키워드 5개 추출
    - 기사 요약: 동일 모델로 기사 본문 내용 100자 이하 텍스트로 요약
    - 벡터 임베딩: Huggingface의 `intfloat/multilingual-e5-large-instruct` 임베딩 모델을 이용하여 1024차원 벡터 생성
    - 카테고리 추론: Zero-shot Learning 방식으로 뉴스 주제를 자동 분류
  3. 전처리된 결과를 PostgreSQL에 저장

#### 2.5.3 실행

```bash
python3 ./transform-and-load/flink.py
```

---

## 3. Backend

### 3.1 구조

```
.
├── accounts
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── articles
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── models.py
```

- PostgreSQL DB (`news`)와 연동

### 3.2 News Articles

- 기존에 만든 `news` 데이터베이스의 `news_articles` 테이블과 `articles` 앱의 `NewsArticle` 모델 연동

### 3.3 Accounts

- `BaseUserManager`, `AbstractBaseUser`를 활용하여 커스텀 유저 모델 제작
  - `username`에 비해 범용성이 더 높은 `email` 기반 로그인
  - 소셜 로그인 연동하여 향후 Google, Naver, Kakao 등 계정으로 로그인할 수 있도록 함
  - 토큰 기반 인증을 바탕으로 보안성 향상

## 4. AI

### 4.1 기사 추천 시스템

- 지금 읽은 기사와 유사한 다른 기사 추천
- 콘텐츠 기반 필터링(content-based filtering)
  - 콘텐츠 자체의 특성과 사용자의 이전 행동 기록을 기반으로 사용자에게 추천
  - 예를 들어, 사용자가 `윤석열`에 대한 기사를 보고 좋아요를 눌렀다면 해당 기사에 대한 분석을 바탕으로 성격이 유사한 다른 기사를 추천함
- 협업 필터링(collaborative filtering)
  - 어떤 아이템에 대해서 비슷한 취향을 가진 사람들이 다른 아이템에 대해서도 비슷한 취향을 가지고 있을 것이라고 가정하고 추천하는 알고리즘
  - 추천의 대상이 되는 사람과 취향이 비슷한 사람들, 즉 neighbour를 찾아 이들이 공통적으로 좋아하는 제품 또는 서비스를 추천 대상인에게 추천하는 것

### 4.2 챗봇 기반 기사 찾기

- 특정 키워드를 입력하면 그에 맞는 기사 추천

### 4.3 RAG
