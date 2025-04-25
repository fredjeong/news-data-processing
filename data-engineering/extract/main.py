from kafka_producer import process_and_send
from rss_reader import get_rss_entries

import sys
from os import path

parent_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(parent_dir)

from config import RSS_FEEDS

def run():
    for journal, url in RSS_FEEDS.items():
        print(f"\n{journal} 기사 수집 중...")
        entries = get_rss_entries(url)
        for entry in entries:
            process_and_send(journal, entry)

if __name__ == "__main__":
    run()
