#!/bin/bash

# Airflow 프로젝트 디렉토리 기준으로 필요한 폴더를 생성하고 권한을 부여하는 스크립트

set -e  # 에러 발생하면 스크립트 즉시 종료

# 현재 위치 표시
echo "현재 작업 디렉토리: $(pwd)"

# 1. 필요한 디렉토리 생성
echo "디렉토리 생성 중..."
mkdir -p ./dags/scripts
mkdir -p ./data
mkdir -p ./output

# 2. 권한 설정 (읽기/쓰기/실행 모두 허용)
echo "디렉토리 권한 설정 중..."
chmod -R 777 ./dags/scripts ./data ./output

# 3. 결과 출력
echo "디렉토리 준비 완료:"
ls -ld ./dags/scripts ./data ./output

# 4. 추가 안내
echo "모든 준비가 완료되었습니다. 이제 docker compose up 하시면 됩니다."
