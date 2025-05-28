import json
import psycopg2
from utils_preprocessing import transform_extract_keywords, transform_to_embedding, transform_classify_category, transform_extract_summary
from utils_elasticsearch import send_to_elasticsearch

import sys
import os
from os import path

root_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

sys.path.append(root_dir)

from config import DB_CONFIG, KAFKA_CONFIG, MODELS_CONFIG

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
    company = data['company']
    content = data['content']
    embedding_dim = MODELS_CONFIG['embedding_dim']
    
    # 날짜 형식 정규화
    try:
        # ISO 8601 타임스탬프 형식 검사 (예: 2025-05-16T13:56:00+09:00)
        if 'T' in data['write_date'] and '+' in data['write_date']:
            # 형식은 그대로 유지 (Elasticsearch에서 인식할 수 있는 형식으로 설정했음)
            pass
        # 다른 형식의 날짜가 있다면 여기서 표준 형식으로 변환
    except Exception as e:
        print(f"날짜 형식 정규화 중 오류: {e}")
        # 날짜 정보가 잘못된 경우 기본값 설정
        data['write_date'] = "2000-01-01"

    # 뉴스 본문이 없는 경우
    if not content:
        data['keywords'] = json.dumps([None for _ in range(5)], ensure_ascii=False)
        title_embedding = [0 for _ in range(embedding_dim)]
        content_embedding = [0 for _ in range(embedding_dim)]
        title_embedding_str = ','.join(map(str, title_embedding))
        content_embedding_str = ','.join(map(str, content_embedding))
        data['title_embedding'] = f"[{title_embedding_str}]"
        data['content_embedding'] = f"[{content_embedding_str}]"
        data['category'] = '미분류'
        data['summary'] = ''
    else:
        data['keywords'] = json.dumps(transform_extract_keywords(content), ensure_ascii=False)
        title_embedding = transform_to_embedding(data['title'])
        title_embedding_str = ','.join(map(str, title_embedding))
        data['title_embedding'] = f"[{title_embedding_str}]"
        data['category'] = transform_classify_category(content)
        data['summary'] = transform_extract_summary(content)
        summary_embedding = transform_to_embedding(data['summary'])
        summary_embedding_str = ','.join(map(str, summary_embedding))
        data['content_embedding'] = f"[{summary_embedding_str}]"
    
    return data

# def save_to_json_file(data, article_id):
#     """기사 데이터를 JSON 파일로 저장"""
#     try:
#         # ./airflow/data/realtime 디렉토리에 기사 저장
#         with open(f"{root_dir}/airflow/data/realtime/article_{article_id}.json", "w") as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)
#         return True
#     except Exception as e:
#         print(f"JSON 파일 저장 실패: {e}")
#         return False 

def save_to_json_file(data, article_id):
    """기사 데이터를 JSON 파일로 저장"""
    try:
        # 디렉토리 존재 확인 및 생성
        save_dir = f"{root_dir}/airflow/data/realtime"
        os.makedirs(save_dir, exist_ok=True)
        
        # 파일 경로 설정
        file_path = f"{save_dir}/article_{article_id}.json"
        
        # 파일 저장
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"JSON 파일 저장 실패: {e}")
        return False
    
def add_to_db(data):
    company = data['company']
    title = data['title']
    writer = data['writer']
    write_date = data['write_date']
    category = data['category']
    content = data['content']
    url = data['url']
    keywords = data['keywords']
    summary = data['summary']
    title_embedding = data['title_embedding']
    content_embedding = data['content_embedding']


    query = f"""
        INSERT INTO {DB_CONFIG['tablename']} (company, title, writer, write_date, category, content, summary, url, keywords, title_embedding, content_embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, vector(%s), vector(%s))
        ON CONFLICT (url) DO NOTHING
        RETURNING id;
        """

    # PostgreSQL 트랜잭션 시작
    conn.autocommit = False  # 자동 커밋 비활성화 
    
    try:
        # SQL INSERT 구문 실행 (news_articles 테이블에 데이터 삽입) 
        cursor.execute(query, (company, title, writer, write_date, category, content, summary, url, keywords, title_embedding, content_embedding))

        # # 변경 사항 저장
        # conn.commit()
        
        # query = f"""
        # SELECT id FROM {DB_CONFIG['tablename']} WHERE url = %s
        # """``
        # cursor.execute(query, (url,))
        # id = cursor.fetchone()[0]
        # # ./airflow/data/realtime 디렉토리에 기사 저장
        # with open(f"{root_dir}/airflow/data/realtime/article_{id}.json", "w") as f:
        #     json.dump(data, f, indent=4, ensure_ascii=False)
        
        # # 저장 성공 메시지 출력
        # print(f"저장 완료: {title}")


        # 영향 받은 행이 있는지 확인 (새 행 삽입 여부)
        if cursor.rowcount > 0:

            # ID 가져오기
            article_id = cursor.fetchone()[0]
            
            # JSON 파일 저장
            save_to_json_file(data, article_id)

            # Elasticsearch에 데이터 전송
            es_success = send_to_elasticsearch(data, article_id)
            


            if es_success:
                # 모든 작업이 성공적으로 완료되면 트랜잭션 커밋
                conn.commit()
                print(f"저장 완료 (PostgreSQL + JSON + Elasticsearch): {title} (ID: {article_id})")
                return data
            else:
                # Elasticsearch 저장 실패 시 롤백
                conn.rollback()
                print(f"Elasticsearch 저장 실패로 트랜잭션 롤백: {title}")
                return data
        else:
            # 중복 URL이거나 삽입이 안 된 경우 - 이미 처리된 데이터
            conn.commit()
            print(f"이미 처리된 URL (중복): {url}")
            return data

    except Exception as e:
        # 오류 발생 시 변경 사항을 롤백
        conn.rollback()  
        
        # 저장 실패 메시지와 오류 이유 출력
        print(f"PostgreSQL 저장 실패: {title}\n이유: {e}")
        return data
    finally:
        # 자동 커밋 다시 활성화
        conn.autocommit = True

