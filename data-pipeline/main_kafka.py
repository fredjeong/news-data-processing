import sys
from os import path

root_dir = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(root_dir)

from config import RSS_FEEDS


utils_dir = path.join(root_dir, 'data-pipeline/utils')
sys.path.append(utils_dir)

from kafka_producer import process_and_send
from rss_reader import get_rss_entries


def run():
    for journal, url in RSS_FEEDS.items():
        print(f"\n{journal} 기사 수집 중...")
        entries = get_rss_entries(url)
        for entry in entries:
            process_and_send(journal, entry)

if __name__ == "__main__":
    run()
