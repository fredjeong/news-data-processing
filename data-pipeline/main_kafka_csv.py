# main/main_kafka_csv.py

import sys
from os import path

root_dir = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(root_dir)


from config import RSS_FEEDS


utils_dir = path.join(root_dir, 'data-pipeline/utils')
sys.path.append(utils_dir)

from kafka_producer import csv_send
from get_bulk_news import get_news_dataframe


def run():
    df = get_news_dataframe()
    print(f'총 {len(df)}건의 기사 수집중...')
    csv_send(df)
        
if __name__ == "__main__":
    run()