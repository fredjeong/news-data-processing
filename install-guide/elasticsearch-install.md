# Elasticsearch 설치 및 설정 가이드

## Docker를 사용한 설치 (권장)

docker-compose.yml 파일이 프로젝트 루트 디렉토리에 있습니다. 다음 명령어로 실행할 수 있습니다:

```bash
cd data-pjt
docker-compose up -d
```

이 설정은 자동으로 Elasticsearch와 Kibana를 설치하고, nori 형태소 분석기 플러그인도 함께 설치합니다.

## 수동 설치 방법

### Elasticsearch 설치

```bash
# 다운로드 및 설치
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.17.1-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.17.1-linux-x86_64.tar.gz
cd elasticsearch-8.17.1/

# 보안 설정 비활성화 (개발 환경용)
echo "xpack.security.enabled: false" >> config/elasticsearch.yml
echo "network.host: 0.0.0.0" >> config/elasticsearch.yml
echo "discovery.seed_hosts: [\"localhost\"]" >> config/elasticsearch.yml
echo "cluster.initial_master_nodes: [\"localhost\"]" >> config/elasticsearch.yml

# nori 플러그인 설치 (한국어 형태소 분석기)
bin/elasticsearch-plugin install analysis-nori

# Elasticsearch 실행
bin/elasticsearch
```

### Kibana 설치 (선택사항)

```bash
wget https://artifacts.elastic.co/downloads/kibana/kibana-8.17.1-linux-x86_64.tar.gz
tar -xzf kibana-8.17.1-linux-x86_64.tar.gz
cd kibana-8.17.1/

# 설정
echo "server.host: 0.0.0.0" >> config/kibana.yml
echo "elasticsearch.hosts: [\"http://localhost:9200\"]" >> config/kibana.yml

# Kibana 실행
bin/kibana
```

## 환경 변수 설정

프로젝트의 .env 파일이나 환경 변수에 다음 설정이 필요합니다:

```bash
# .env 파일 설정 예시
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=elastic123
```

## 테스트

Elasticsearch가 정상적으로 동작하는지 확인:

```bash
curl http://localhost:9200
```

Nori 플러그인이 정상적으로 설치되었는지 확인:

```bash
curl -X GET "localhost:9200/_cat/plugins"
``` 