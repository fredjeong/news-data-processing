# Airflow 설치

- [Docker 설치 (이미 설치되었을 경우 무시)](./docker-install.md)

```bash
# Airflow 프로젝트 디렉토리 생성
mkdir airflow
cd airflow

# airflow docker-compose 다운로드
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.5/docker-compose.yaml' 

# 서브 디렉토리 생성
mkdir -p ./dags ./logs ./plugins ./config

# 환경 변수 파일 생성 (AIRFLOW_UID 지정)
echo -e "AIRFLOW_UID=$(id -u)" > .env

# 디렉토리 권한 설정 (Airflow 로그 및 DAG 접근 오류 방지)
sudo chmod -R 777 ./logs ./dags ./plugins ./config
```

# Airflow 실행

```bash
# 초기화 실행 (metadata DB 초기화 등)
sudo docker compose up airflow-init

# 서비스 시작 (백그라운드 실행 가능)
sudo docker compose up -d
```