import json
import psycopg2
from utils_preprocessing import transform_extract_keywords, transform_to_embedding, transform_classify_category, transform_extract_summary

import sys
from os import path

parent_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(parent_dir)

from config import DB_CONFIG

# 전처리 및 저장 파이프라인 구성

# PostgreSQL 데이터베이스 연결 설정
conn = psycopg2.connect(
    dbname=DB_CONFIG['dbname'],  # 데이터베이스 이름
    user=DB_CONFIG['user'],  # 사용자 이름
    password=DB_CONFIG['password'],  # 비밀번호
    host=DB_CONFIG['host'],  # 호스트 주소 (여기서는 로컬 호스트)
    port=DB_CONFIG['port']  # 포트 번호
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
        data['summary'] = ''
    else:
        data['keywords'] = json.dumps(transform_extract_keywords(content), ensure_ascii=False)
        embedding = transform_to_embedding(content)
        embedding_str = ','.join(map(str, embedding))
        data['embedding'] = f"'[{embedding_str}]'"
        data['category'] = transform_classify_category(content)
        data['summary'] = transform_extract_summary(content)
    
    return data


def add_to_db(data):
    title = data['title']
    writer = data['writer']
    write_date = data['write_date']
    category = data['category']
    content = data['content']
    url = data['url']
    keywords = data['keywords']
    summary = data['summary']
    embedding = data['embedding']


    # Use psycopg2's mogrify to properly escape special characters
    query = cursor.mogrify(f"""
        INSERT INTO {DB_CONFIG['tablename']} (title, writer, write_date, category, content, summary, url, keywords, embedding) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, vector(%s))
        ON CONFLICT (url) DO NOTHING;
        """, 
        (title, writer, write_date, category, content, summary, url, keywords, embedding)
    ).decode()

    # query = f"""
    #     INSERT INTO {DB_CONFIG['tablename']} (title, writer, write_date, category, content, summary, url, keywords, embedding)
    #     VALUES ('{title}', '{writer}', '{write_date}', '{category}', '{content}', '{summary}', '{url}', '{keywords}', vector({embedding}))
    #     ON CONFLICT (url) DO NOTHING;
    #     """

    try:
        # SQL INSERT 구문 실행 (news_articles 테이블에 데이터 삽입) 
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