# SSAFYNEWS Airflow

## 📖 프로젝트 개요

SSAFYNEWS Airflow는 뉴스 데이터 파이프라인을 자동화하고 관리하는 워크플로우 오케스트레이션 시스템입니다. \
Apache Airflow를 기반으로 하여 뉴스 수집, 처리, 분석 및 리포트 생성을 자동화하며, HDFS와 연동하여 대용량 데이터를 효율적으로 관리합니다.

## 🚀 주요 기능

### 📊 데이터 파이프라인 자동화
- **일일 뉴스 리포트 생성**: 매일 새벽 1시 자동 실행
- **Spark 기반 데이터 처리**: 대용량 뉴스 데이터 분석
- **키워드 빈도 분석**: 뉴스 키워드 추출 및 시각화
- **이메일 알림**: 분석 결과 자동 전송

### 🗄️ 분산 데이터 저장
- **HDFS 연동**: 처리된 데이터를 HDFS에 자동 저장
- **데이터 아카이빙**: 로컬 → HDFS 자동 이관
- **분석 결과 저장**: 키워드 분석 결과 HDFS 저장

### 📈 모니터링 및 관리
- **Airflow Web UI**: 워크플로우 시각화 및 모니터링
- **작업 스케줄링**: Cron 기반 자동 실행
- **에러 처리**: 재시도 로직 및 알림

## 🛠 기술 스택

### Core Framework
- **Apache Airflow 2.10.5**: 워크플로우 오케스트레이션  
- **Apache Spark 3.5.4**: 대용량 데이터 처리
- **Apache Hadoop HDFS**: 분산 파일 시스템

### 데이터베이스
- **PostgreSQL 13**: 메타데이터 저장
- **Redis 7.2**: Celery 브로커

### 컨테이너화
- **Docker & Docker Compose**: 컨테이너 오케스트레이션
- **CeleryExecutor**: 분산 작업 실행

### 데이터 처리
- **PySpark**: Python Spark API
- **Matplotlib**: 데이터 시각화
- **Pandas**: 데이터 분석

## 📁 프로젝트 구조

```
airflow/
├── dags/                           # Airflow DAG 파일
│   ├── scripts/                    # 실행 스크립트
│   │   └── spark_daily_report.py  # Spark 일일 리포트 (HDFS 연동)
│   └── daily_report_dag.py        # 일일 리포트 DAG
├── data/                          # 로컬 데이터 저장소
│   ├── realtime/                  # 실시간 JSON 데이터
│   ├── news_archive/              # 처리 완료 데이터
│   └── *.png, *.csv              # 분석 결과 파일
├── logs/                          # Airflow 로그
├── config/                        # 설정 파일
├── plugins/                       # Airflow 플러그인
├── output/                        # 출력 파일
├── docker-compose-airflow.yaml    # Docker Compose 설정
├── Dockerfile.airflow             # Airflow 컨테이너 설정
├── Dockerfile.spark               # Spark 컨테이너 설정
└── setup.sh                      # 초기 설정 스크립트
```

## 🔧 설치 및 실행

### 사전 요구사항
- Docker 20.0.0 이상
- Docker Compose 2.0.0 이상
- 최소 8GB RAM 권장
- HDFS 클러스터 (선택사항)

### 초기 설정
```bash
# 1. 필요한 디렉토리 생성 및 권한 설정
chmod +x setup.sh
./setup.sh

# 2. 환경 변수 설정 (선택사항)
export AIRFLOW_UID=50000
export AIRFLOW_PROJ_DIR=.
```

### 서비스 시작
```bash
# 1. 컨테이너 빌드 및 시작
docker-compose -f docker-compose-airflow.yaml up -d

# 2. Airflow 초기화 (최초 실행 시)
docker-compose -f docker-compose-airflow.yaml up airflow-init

# 3. 모든 서비스 시작
docker-compose -f docker-compose-airflow.yaml up -d
```

### 서비스 접속
- **Airflow Web UI**: http://localhost:8080
  - Username: `airflow`
  - Password: `airflow`
- **PostgreSQL**: localhost:5433
  - Username: `airflow`
  - Password: `airflow`
  - Database: `airflow`

### 서비스 중지
```bash
# 서비스 중지
docker-compose -f docker-compose-airflow.yaml down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose -f docker-compose-airflow.yaml down -v
```

## 📊 DAG 구조

### daily_report_dag
매일 새벽 1시에 실행되는 일일 뉴스 분석 워크플로우

```python
# 스케줄: 매일 새벽 1시 (KST)
schedule_interval='0 1 * * *'

# 작업 흐름
spark_daily_report → notify_report_generated → send_email
```

#### 작업 단계
1. **spark_daily_report**: Spark를 이용한 뉴스 키워드 분석 및 HDFS 저장
2. **notify_report_generated**: 리포트 생성 완료 알림
3. **send_email**: 분석 결과 이메일 전송

## 🔄 데이터 파이프라인

### 배치 데이터 처리 (Spark + HDFS)
```
JSON 파일 → Spark 분석 → 로컬 저장 → HDFS 저장(로컬 삭제) → 아카이브
```

#### spark_daily_report.py 주요 기능
- **데이터 수집**: `/opt/airflow/data/realtime/*.json` 파일 처리
- **키워드 분석**: 뉴스 키워드 빈도 분석 및 시각화
- **로컬 저장**: CSV, PNG 파일 생성
- **HDFS 연동**: 처리된 데이터를 HDFS에 자동 저장
- **아카이빙**: 처리 완료된 파일을 로컬 아카이브로 이동

### HDFS 저장 구조
```
hdfs://namenode:8020/news_archive/
├── 2025-01-15/                    # 날짜별 디렉토리
│   ├── news_001.json             # 원본 뉴스 데이터
│   ├── news_002.json
│   └── reports/                   # 분석 결과
│       └── keyword_counts/        # 키워드 빈도 데이터
└── 2025-01-16/
    └── ...
```

## 🐳 Docker 구성

### 서비스 구성
- **airflow-webserver**: Airflow Web UI (포트 8080)
- **airflow-scheduler**: DAG 스케줄러
- **airflow-worker**: Celery 워커
- **airflow-triggerer**: 트리거 서비스
- **postgres**: 메타데이터 저장소 (포트 5433)
- **redis**: Celery 브로커

### 컨테이너 설정

#### Dockerfile.airflow
```dockerfile
FROM apache/airflow:2.10.5
# Java 17, Spark 3.5.4, 한글 폰트 설치
# PySpark, matplotlib 등 Python 패키지 설치
# HDFS 클라이언트 설정
```

#### Dockerfile.spark
```dockerfile
FROM bitnami/spark:3.5.4
# matplotlib, 한글 폰트 설치
# 데이터 시각화를 위한 환경 구성
```

## 📈 모니터링 및 로깅

### Airflow Web UI 기능
- **DAG 실행 상태 모니터링**
- **작업 로그 확인**
- **스케줄 관리**
- **변수 및 연결 설정**

### 로그 관리
- 모든 작업 로그는 `./logs` 디렉토리에 저장
- 날짜별, DAG별로 구분된 로그 파일
- 실시간 로그 스트리밍 지원

### 헬스체크
- 각 서비스별 헬스체크 설정
- 자동 재시작 정책
- 의존성 기반 서비스 시작 순서

## 🔧 설정 및 커스터마이징

### 환경 변수
```yaml
# Airflow 설정
AIRFLOW__CORE__EXECUTOR: CeleryExecutor
AIRFLOW__CORE__DEFAULT_TIMEZONE: Asia/Seoul
AIRFLOW__CORE__LOAD_EXAMPLES: 'false'

# 데이터베이스 설정
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow

# Celery 설정
AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0
```

### HDFS 설정
```python
# Spark 세션 HDFS 설정
HDFS_BASE_PATH = "hdfs://namenode:8020"
HDFS_ARCHIVE_PATH = f"{HDFS_BASE_PATH}/news_archive"

# Spark 설정
.config("spark.hadoop.fs.defaultFS", "file:///")
.config("spark.hadoop.dfs.client.use.datanode.hostname", "true")
.config("spark.hadoop.dfs.datanode.use.datanode.hostname", "true")
```

### 볼륨 마운트
```yaml
volumes:
  - ./dags:/opt/airflow/dags              # DAG 파일
  - ./logs:/opt/airflow/logs              # 로그 파일
  - ./data:/opt/airflow/data              # 데이터 파일
  - ./output:/opt/airflow/output          # 출력 파일
```

### 이메일 설정 (선택사항)
- DAG 내의 send_email을 사용하기 위한 설정
```yaml
# SMTP 설정 (주석 해제 후 사용)
  # AIRFLOW__SMTP__SMTP_HOST: 'smtp.gmail.com'
  # AIRFLOW__SMTP__SMTP_USER: '{gmail 계정}'
  # AIRFLOW__SMTP__SMTP_PASSWORD: '{app 비밀번호}'
  # AIRFLOW__SMTP__SMTP_PORT: 587
  # AIRFLOW__SMTP__SMTP_MAIL_FROM: '{gmail 계정}'
```


## 📊 데이터 흐름

### 입력 데이터
- **JSON 파일**: `/opt/airflow/data/realtime/*.json`
- **뉴스 메타데이터**: 제목, 내용, 키워드, 작성일 등

### 처리 과정
1. **수집**: JSON 파일 스캔 및 로드
2. **분석**: Spark를 이용한 키워드 빈도 분석
3. **시각화**: matplotlib을 이용한 차트 생성
4. **로컬 저장**: CSV, PNG 파일 생성
5. **HDFS 저장**: 원본 데이터 및 분석 결과 HDFS 저장
6. **아카이브**: 처리 완료 파일 로컬 아카이브로 이동

### 출력 결과
- **로컬 파일**:
  - `keyword_frequency_{date}.png`: 키워드 빈도 차트
  - `keyword_frequency_{date}.csv`: 키워드 빈도 데이터
- **HDFS 파일**:
  - `/news_archive/{date}/*.json`: 원본 뉴스 데이터
  - `/news_archive/{date}/reports/keyword_counts/`: 분석 결과
- **이메일 리포트**: 일일 분석 결과

## 🐛 트러블슈팅

### 자주 발생하는 문제

1. **권한 문제**
   ```bash
   # 디렉토리 권한 설정
   chmod -R 777 ./dags ./data ./output ./logs

   # permission denied 발생 시 소유권 설정
   sudo chown {user}:{user} ./dags ./data ./output ./logs
   ```

2. **spark에서 json을 읽어오지 못하는 문제**
    ```bash
    # 여러 줄의 json을 읽기 위해 multiLine=True 사용
    df = spark.read.json(f"file://{local_path}",multiLine=True)
    ```

### 로그 확인
```bash
# Airflow 로그 확인
docker-compose -f docker-compose-airflow.yaml logs airflow-scheduler

# 특정 서비스 로그 확인
docker-compose -f docker-compose-airflow.yaml logs -f airflow-worker

# 컨테이너 내부 접속
docker exec -it airflow_airflow-worker_1 bash
```

## 🔄 개발 가이드

### DAG 개발
1. `dags/` 디렉토리에 Python 파일 생성
2. DAG 정의 및 작업 구성
3. Airflow Web UI에서 DAG 활성화

### 스크립트 개발
1. `dags/scripts/` 디렉토리에 스크립트 작성
2. 필요한 Python 패키지 Dockerfile에 추가
3. 컨테이너 재빌드 후 테스트

### HDFS 연동 개발
```python
# HDFS 디렉토리 생성
hadoop = spark._jvm.org.apache.hadoop.fs.FileSystem.get(
    spark.sparkContext._jsc.hadoopConfiguration()
)
hdfs_path = spark._jvm.org.apache.hadoop.fs.Path(hdfs_date_path)
if not hadoop.exists(hdfs_path):
    hadoop.mkdirs(hdfs_path)

# 데이터 저장
df.write.mode("overwrite").json(hdfs_target_path)
```


## 📝 향후 개선 사항
###실시간 데이터 스트리밍

