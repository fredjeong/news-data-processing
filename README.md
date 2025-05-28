# AI 기반 맞춤형 뉴스 플랫폼

## 1. 개요

본 프로젝트는 실시간으로 업데이트되는 국내 주요 언론사들의 뉴스 데이터를 수집하고 분석하여 사용자에게 가치 있는 정보를 제공하는 지능형 뉴스 플랫폼입니다. 최신 빅데이터 기술과 인공지능을 활용하여 방대한 뉴스 데이터를 효율적으로 처리하고, 사용자 개개인에게 맞춤화된 뉴스 경험을 제공합니다.

핵심 기능으로는 실시간 뉴스 수집 및 아카이빙, 개인화된 뉴스 추천 시스템, 그리고 최신 LLM 기술을 활용한 기사 요약 서비스가 있습니다. 사용자들은 관심 있는 기사에 대해 좋아요와 스크랩 기능을 통해 상호작용할 수 있으며, 이러한 활동 데이터는 추천 시스템을 더욱 정교화하는데 활용됩니다. 특히, 한국어 특화 LLM을 통해 고품질의 기사 요약과 관련 정보를 제공받을 수 있어, 빠르고 효율적인 뉴스 소비가 가능합니다.

이 프로젝트는 현대인의 정보 소비 패턴을 고려한 사용자 중심의 뉴스 플랫폼을 지향하며, 지속적인 기술 혁신을 통해 더 나은 뉴스 경험을 제공하고자 합니다.

## 2. 프로젝트 구조

```
.
├── README.md
├── __init__.py
├── airflow
├── architecture.txt
├── backend
├── config.py
├── data
├── docker-compose.yml
├── flink-sql-connector-kafka-3.3.0-1.20.jar
├── frontend
├── install-guide
├── logstash
├── preprocessing
├── package-lock.json
├── requirements-mac.txt
├── requirements-win.txt
```

## 3. 환경 설정 및 설치 가이드

- 권장 파이썬 버전: 3.10
- 필수 라이브러리 설치
  ```bash
  pip install -r requirements-win.txt # Windows
  pip install -r requirements-mac.txt # Mac
  ```
- 개별 설치 가이드
  - [Docker](./install-guide/docker-install.md)
  - [Java](./install-guide/java-install.md)
  - [Kafka](./install-guide/kafka-install.md)
  - [Flink](./install-guide/flink-install.md)
  - [Spark](./install-guide/spark-install.md)
  - [PostgreSQL](./install-guide/postgresql-install.md)
  - [Airflow](./install-guide/airflow-install.md)
  - [ElasticSearch](./install-guide/elasticsearch-install.md)
  - [Ollama](./install-guide/ollama-install.md)
  - [Django](./install-guide/django-install.md)

## 4. 서비스별 주요 기능 및 기술 스택

- [Data Pipeline 설명 문서](./data-pipeline/README.md)
- [Backend/AI 설명 문서](./backend/README.md)
- [Frontend 설명 문서](./frontend/README.md)

## 5. 개발자

- 노규백 (팀장 | Frontend)
- 정찬영 (팀원 | Backend)
