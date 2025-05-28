import sys
import argparse
import os
import shutil
from datetime import datetime, timedelta

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, count, from_json, to_timestamp, to_date, split, trim, regexp_replace
from pyspark.sql.types import ArrayType, StringType, StructType, StructField
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import json

def main(report_date_str):
    print(f"시작 날짜: {report_date_str}")
    
    # 폰트 설정 (기본 폰트)
    FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    
    # 로컬 realtime 데이터 경로
    REALTIME_DIR = "/opt/airflow/data/realtime"
    # 로컬 archive 데이터 경로
    ARCHIVE_DIR = "/opt/airflow/data/news_archive"
    # 로컬 report 데이터 경로
    REPORT_DIR = "/opt/airflow/data"
    # HDFS 기본 경로
    HDFS_BASE_PATH = "hdfs://namenode:8020"
    # HDFS archive 경로
    HDFS_ARCHIVE_PATH = f"{HDFS_BASE_PATH}/news_archive"

    # font 설정
    font_prop = fm.FontProperties(fname=FONT_PATH, size=12)
    
    try:
        # 입력 디렉토리 확인
        if not os.path.exists(REALTIME_DIR):
            print(f"Error: Input directory {REALTIME_DIR} does not exist")
            return
            
        # JSON 파일 목록 확인
        json_files = [f for f in os.listdir(REALTIME_DIR) if f.endswith('.json')]
        if not json_files:
            print(f"Error: No JSON files found in {REALTIME_DIR}")
            return
            
        print(f"Found {len(json_files)} JSON files in {REALTIME_DIR}")
        
        # spark 세션 생성
        spark = SparkSession.builder \
                .appName("DailyNewsReport") \
                .config("spark.hadoop.fs.defaultFS", HDFS_BASE_PATH) \
                .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
                .config("spark.hadoop.dfs.datanode.use.datanode.hostname", "true") \
                .config("spark.hadoop.dfs.namenode.datanode.registration.ip-hostname-check", "false") \
                .getOrCreate()
         
        # 입력된 날짜의 하루 전 날짜 계산
        report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
        target_date = (report_date - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"분석 대상 날짜: {target_date}")
        
        # JSON 파일들을 하나씩 읽어서 처리
        all_data = []
        for json_file in json_files:
            file_path = os.path.join(REALTIME_DIR, json_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.append(data)
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
                continue
        
        if not all_data:
            print("No valid JSON data found")
            return
            
        # DataFrame 생성
        df = spark.createDataFrame(all_data)
        print("JSON 스키마:")
        print(df.printSchema())
        
        # 날짜 필터링 (to_date 함수 사용)
        target_df = df.filter(to_date(col("write_date")) == target_date)
        article_count = target_df.count()
        print(f"분석 대상 기사 수: {article_count}")

        if article_count == 0:
            print("해당 날짜의 기사가 없습니다.")
            return 
        
        # 키워드 분석
        keywords_df = target_df.select(
            explode(
                split(
                    regexp_replace(
                        regexp_replace(col("keywords"), '[^가-힣a-zA-Z0-9]', ' '),  # 한국어, 영어, 숫자만 남기고 나머지는 공백으로
                        '\\s+', ' '  # 여러 공백을 하나로
                    ),
                    ' '  # 공백으로 분리
                )
            ).alias("keyword")
        )
        # 공백 제거
        keywords_df = keywords_df.select(trim(col("keyword")).alias("keyword"))
        # 빈 문자열 제거
        keywords_df = keywords_df.filter(col("keyword") != "")
        
        keyword_counts = keywords_df.groupBy("keyword") \
            .agg(count("*").alias("count")) \
            .orderBy(col("count").desc()) \
            .limit(10)  # 상위 10개 키워드만 추출
        
        print("\n키워드 빈도 분석 결과 (상위 10개):")
        keyword_counts.show(truncate=False)
        
        # 키워드 빈도 시각화
        plt.figure(figsize=(12, 8))
        keywords = keyword_counts.select("keyword").rdd.flatMap(lambda x: x).collect()
        counts = keyword_counts.select("count").rdd.flatMap(lambda x: x).collect()
        plt.bar(keywords, counts, color="skyblue")
        
        plt.xlabel("키워드", fontproperties=font_prop)
        plt.ylabel("빈도", fontproperties=font_prop)
        plt.title(f"{target_date} 키워드 빈도 분석 (상위 10개)", fontproperties=font_prop)
        
        # x축 레이블에 폰트 적용 및 회전
        plt.xticks(rotation=45, fontproperties=font_prop)
        
        plt.tight_layout()  # 레이블이 잘리지 않도록 조정
        plt.savefig(os.path.join(REPORT_DIR, f"keyword_frequency_{target_date}.png"))
        plt.close()
        
        # 키워드 빈도 데이터 저장
        keyword_counts_df = keyword_counts.toPandas()
        keyword_counts_df.to_csv(os.path.join(REPORT_DIR, f"keyword_frequency_{target_date}.csv"), index=False)
        
        # 처리된 파일을 archive로 이동
        for filename in os.listdir(REALTIME_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(REALTIME_DIR, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                
                    write_date = data.get("write_date")
                    
                    if write_date and write_date[:10] == target_date:
                        source_path = os.path.join(REALTIME_DIR, filename)
                        target_path = os.path.join(ARCHIVE_DIR, filename)
                        shutil.move(source_path, target_path)
                        print(f"Moved {filename} to archive ({write_date[:10]})")
                except Exception as e:
                    print(f"Error {filename}: {e}")
        
        # 처리된 파일을 hdfs에 저장
        hdfs_date_path = f"{HDFS_ARCHIVE_PATH}/{target_date}"
        
        # HDFS 디렉토리 생성
        spark.sparkContext._jsc.hadoopConfiguration().set("fs.defaultFS", HDFS_BASE_PATH)
        hadoop = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark.sparkContext._jsc.hadoopConfiguration())
        hdfs_path = spark._jvm.org.apache.hadoop.fs.Path(hdfs_date_path)
        if not hadoop.exists(hdfs_path):
            hadoop.mkdirs(hdfs_path)
            print(f"Created HDFS directory: {hdfs_date_path}")
        
        # archive 디렉토리의 파일들을 HDFS에 저장
        for filename in os.listdir(ARCHIVE_DIR):
            if filename.endswith('.json'):
                try:
                    local_path = os.path.join(ARCHIVE_DIR, filename)
                    hdfs_target_path = f"{hdfs_date_path}/{filename}"
                    
                    # JSON 파일을 HDFS에 복사
                    df = spark.read.json(f"file://{local_path}",multiLine=True)
                    df.write.mode("overwrite").json(hdfs_target_path)
                    print(f"Saved {filename} to HDFS: {hdfs_target_path}")
                    
                except Exception as e:
                    print(f"Error saving {filename} to HDFS: {e}")
                    continue
        
        # 분석 결과도 HDFS에 저장
        hdfs_report_path = f"{hdfs_date_path}/reports"
        keyword_counts.write.mode("overwrite").csv(f"{hdfs_report_path}/keyword_counts")
        print(f"Saved analysis results to HDFS: {hdfs_report_path}")
        
        # HDFS 저장 후 news_archive 폴더 비우기
        for filename in os.listdir(ARCHIVE_DIR):
            file_path = os.path.join(ARCHIVE_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed {filename} from archive")
            except Exception as e:
                print(f"Error removing {filename}: {e}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    today = datetime.today().strftime('%Y-%m-%d')
    
    # python report.py --date 2025-05-01 과 같이 명령행 인자를 사용하기 위함
    parser = argparse.ArgumentParser(description="Spark를 이용한 일일 뉴스 리포트 생성")
    parser.add_argument("--date", default=today, help="보고서 기준 날짜 (YYYY-MM-DD)")
    args = parser.parse_args()
    main(args.date)


'''
airflow/
├── dags/
│   └── scripts/
│       └── spark_daily_report.py     ← 이 파일 위치
├── data/                            ← PDF 리포트 저장
│   ├── realtime/                     ← JSON 원본 데이터
│   └── news_archive/                ← 처리 완료된 파일 이동                       


mkdir -p dags/scripts         # Spark 스크립트
mkdir -p data/realtime        # JSON 수신
mkdir -p data/news_archive    # 이동 대상
mkdir -p data              # PDF 출력

'''
