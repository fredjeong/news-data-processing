import random
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from articles.models import NewsArticle

CATEGORIES = ['정치', '경제', '사회', '문화', '기술', '스포츠', '연예']
KEYWORDS_POOL = [
    "경제", "정치", "사회", "기술", "문화", "환경", "교육", "의료", "스포츠", "연예",
    "국제", "과학", "산업", "노동", "복지", "여행", "음식", "예술", "자동차", "부동산"
]

def random_keywords():
    return json.dumps(random.sample(KEYWORDS_POOL, 5), ensure_ascii=False)

class Command(BaseCommand):
    help = '뉴스 기사 더미 데이터 50개 생성'

    def handle(self, *args, **kwargs):
        for i in range(50):
            NewsArticle.objects.create(
                company=f"테스트 기업 {i%5+1}",
                title=f"테스트 뉴스 기사 {i+1}",
                writer=f"기자{i%5+1}",
                write_date=timezone.now(),
                category=random.choice(CATEGORIES),
                content=f"이것은 테스트 뉴스 기사 본문입니다. 번호: {i+1}",
                summary=f"테스트 뉴스 기사 {i+1}의 요약입니다.",
                url=f"https://news.example.com/article/{i+1}",
                keywords=random_keywords(),
                title_embedding="[" + ",".join([str(random.random()) for _ in range(1024)]) + "]",
                content_embedding="[" + ",".join([str(random.random()) for _ in range(1024)]) + "]",
            )
        self.stdout.write(self.style.SUCCESS('더미 뉴스 기사 50개가 성공적으로 생성되었습니다.'))
