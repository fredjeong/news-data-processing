# PostgreSQL 16 및 pgvector 설치

### PostgreSQL 설치

```bash
brew install postgresql@16

echo 'export POSTGRESQL_HOME=/opt/homebrew/opt/postgresql@16' >> ~/.zshrc
echo 'export PATH=$POSTGRESQL_HOME/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

brew services start postgresql@16 # 시작
brew services stop postgresql@16 # 종료
psql postgres # PostgreSQL 접속
```

### 접속 인증 설정 (`pg_hba.conf` 수정)

```bash
vim /opt/homebrew/var/postgresql@16/pg_hba.conf
```

아래와 같이 수정

```
# "local" is for Unix domain socket connections only
local   all             all                                     md5
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     md5
host    replication     all             127.0.0.1/32            md5
host    replication     all             ::1/128                 md5
```

### pgvector 설치

```bash
cd /tmp
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install # may need sudo
```

### 접속

```bash
psql -U postgres
```

### DB 생성 및 접속

```bash
CREATE DATBASE news;
```

### DB 접속 및 테이블 생성

```bash
\c news

-- pgvector 확장 설치 (최초 1회)
CREATE EXTENSION IF NOT EXISTS vector;

-- news_articles 테이블 생성
CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    company VARCHAR(200) NOT NULL,
    title VARCHAR(200) NOT NULL,
    writer VARCHAR(255) NOT NULL,
    write_date TIMESTAMP NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    url VARCHAR(200) UNIQUE NOT NULL,
    keywords JSON DEFAULT '[]'::json,
    title_embedding VECTOR(1024) NOT NULL,
    content_embedding VECTOR(1024) NOT NULL
);
```

### [Optional] 신규 유저 생성 및 권한 부여

```bash
psql postgres

CREATE USER new-user WITH PASSWORD 'new-user';
GRANT ALL PRIVILEGES ON DATABASE news TO new-user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO new-user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO new-user;
GRANT CREATE ON SCHEMA public TO new-user;

\c news

GRNAT ALL PRIVILEGES ON TABLE news_article TO new-user;
GRANT ALL ON TABLE news_article TO new-user;
GRANT ALL ON SEQUENCE news_article_id_seq TO new-user;
```