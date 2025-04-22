import json
from dotenv import load_dotenv
import os
import psycopg2
from utils_preprocessing import transform_extract_keywords, transform_to_embedding, transform_classify_category


load_dotenv()

API_KEY = os.environ.get('OPENAI_API_KEY')
USERID = os.environ.get('POSTGRESQL_USERID')
PASSWORD = os.environ.get('POSTGRESQL_PASSWORD')
# 전처리 및 저장 파이프라인 구성
"""
1. 데이터 접수 (json)
2. 나머지는 다 냅두고, json의 content 항목에 대해서
    2.1 키워드 추출 (keywords 리스트)
    2.2 벡터 임베딩 (길이 1536인 리스트)
    2.3 카테고리 분류 (문자열)
3. 이렇게 새로 얻은 애들을 json에 추가해야 함
4. 각 항목을 PostgreSQL에 적재
"""

# PostgreSQL 데이터베이스 연결 설정
conn = psycopg2.connect(
    dbname='news',  # 데이터베이스 이름
    user=USERID,  # 사용자 이름
    password=PASSWORD,  # 비밀번호
    host='localhost',  # 호스트 주소 (여기서는 로컬 호스트)
    port=5432  # 포트 번호
)
cursor = conn.cursor()  # 데이터베이스와 상호 작용하기 위한 커서 객체 생성

def preprocess(data):
    data = json.loads(data)
    content = data['content']
    embedding_dim = 1536

    # 뉴스 본문이 없는 경우
    if not content:
        data['keywords'] = json.dumps([None for _ in range(5)], ensure_ascii=False)
        embedding = [0 for _ in range(embedding_dim)]
        embedding_str = ','.join(map(str, embedding))
        data['embedding'] = f"'[{embedding_str}]'"
        data['category'] = '미분류'
    else:
        data['keywords'] = json.dumps(transform_extract_keywords(content), ensure_ascii=False)
        embedding = transform_to_embedding(content)
        embedding_str = ','.join(map(str, embedding))
        data['embedding'] = f"'[{embedding_str}]'"
        data['category'] = transform_classify_category(content)
    
    return data


def add_to_db(data):
    title = data['title']
    writer = data['writer']
    write_date = data['write_date']
    category = data['category']
    content = data['content']
    url = data['url']
    keywords = data['keywords']
    embedding = data['embedding']

    query = f"""
        INSERT INTO news_articles (title, writer, write_date, category, content, url, keywords, embedding)
        VALUES ('{title}', '{writer}', '{write_date}', '{category}', '{content}', '{url}', '{keywords}', vector({embedding}))
        ON CONFLICT (url) DO NOTHING;
        """

    try:
        # SQL INSERT 구문 실행 (news_article 테이블에 데이터 삽입) 
        cursor.execute(query)

        # 변경 사항 저장
        conn.commit()

        # 저장 성공 메시지 출력
        print(f"저장 완료: {title}")  

    except Exception as e:
        # 오류 발생 시 변경 사항을 롤백
        conn.rollback()  
        
        # 저장 실패 메시지와 오류 이유 출력
        print(f"저장 실패: {title}\n이유: {e}") 