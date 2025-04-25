import feedparser  # RSS 피드 데이터를 파싱하는 데 사용되는 라이브러리입니다.

def get_rss_entries(url: str):
    try:
        return feedparser.parse(url)['entries']
    except Exception as e:
        print(f"[Error] RSS 파싱 실패: {e}")
        return []
