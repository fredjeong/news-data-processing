<script setup>
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import { computed } from "vue";

const props = defineProps({
  article: {
    type: Object,
    required: true,
  },
  searchQuery: {
    type: String,
    default: ''
  }
});

const { formatDate } = useDate();
const date = computed(() => formatDate(props.article.write_date));

// 키워드 처리 함수
const processedKeywords = computed(() => {
  if (!props.article.keywords) return [];
  
  // 키워드가 이미 배열인 경우
  if (Array.isArray(props.article.keywords)) {
    return props.article.keywords.slice(0, 5); // 최대 5개만 표시
  }
  
  // 키워드가 문자열인 경우 (JSON 문자열)
  try {
    if (typeof props.article.keywords === 'string') {
      // JSON 형식으로 파싱 시도
      const parsed = JSON.parse(props.article.keywords);
      return Array.isArray(parsed) ? parsed.slice(0, 5) : [];
    }
  } catch (e) {
    // 파싱 실패 시 정규식으로 추출
    const extracted = props.article.keywords.match(/'([^']+)'/g)?.map(tag => tag.replace(/'/g, '')) || [];
    return extracted.slice(0, 5);
  }
  
  return [];
});

// 카테고리별 이모지 매핑
const getCategoryEmoji = (category) => {
  const emojiMap = {
    '정치': '🏛️',
    '경제': '💰',
    '사회': '🏘️',
    '국제': '🌍',
    '문화': '🎭',
    '연예': '🎬',
    '스포츠': '⚽',
    '과학': '🔬',
    '기술': '💻',
    'IT': '📱',
    '건강': '🏥',
    '환경': '🌱',
    '교육': '📚',
    '여행': '✈️',
    '음식': '🍽️',
    '패션': '👗',
    '자동차': '🚗',
    '부동산': '🏠'
  };
  return emojiMap[category] || '📰';
};

// 요약문 생성
const getSummary = computed(() => {
  if (props.article.summary) {
    return props.article.summary.length > 150 
      ? props.article.summary.substring(0, 150) + '...'
      : props.article.summary;
  }
  return props.article.content 
    ? props.article.content.substring(0, 150) + '...'
    : '요약 정보가 없습니다.';
});

const highlightText = (text) => {
  if (!props.searchQuery || !text) return text;
  
  const regex = new RegExp(`(${props.searchQuery})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
};

const highlightedTitle = computed(() => highlightText(props.article.title));
const highlightedSummary = computed(() => highlightText(props.article.summary));
</script>

<template>
  <article class="news-card">
    <!-- 카드 헤더 -->
    <header class="card-header">
      <div class="category-badge">
        <span class="category-emoji">{{ getCategoryEmoji(article.category) }}</span>
        <span class="category-text">{{ article.category }}</span>
      </div>
      <div class="meta-info">
        <div class="author">
          <span class="author-icon">✍️</span>
          <span class="author-name">{{ article.writer }}</span>
        </div>
        <div class="date">
          <span class="date-icon">📅</span>
          <span class="date-text">{{ date }}</span>
        </div>
      </div>
    </header>

    <!-- 카드 콘텐츠 -->
    <RouterLink :to="{ name: 'newsDetail', params: { id: article.id } }" class="card-content">
      <h2 class="news-title" v-html="highlightedTitle"></h2>
      <p class="news-summary" v-html="highlightedSummary"></p>
      <div class="read-more">
        <span>자세히 읽기</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </RouterLink>

    <!-- 카드 푸터 -->
    <footer class="card-footer">
      <div class="engagement-stats">
        <div class="stat-item">
          <span class="stat-icon">❤️</span>
          <span class="stat-value">{{ article.like_count || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">👀</span>
          <span class="stat-value">{{ article.view_count || 0 }}</span>
        </div>
        <a :href="article.url" target="_blank" class="external-link" title="원문 보기">
          <span class="stat-icon">🔗</span>
          <span>원문</span>
        </a>
      </div>

      <div class="keywords" v-if="processedKeywords.length > 0">
        <div class="keywords-label">
          <span class="keywords-icon">🏷️</span>
          <span>키워드</span>
        </div>
        <div class="keywords-list">
          <span 
            v-for="(keyword, index) in processedKeywords.slice(0, 4)" 
            :key="index" 
            class="keyword-tag"
            :class="`keyword-theme-${(index % 4) + 1}`"
          >
            #{{ keyword }}
          </span>
          <span v-if="processedKeywords.length > 4" class="more-tags">
            +{{ processedKeywords.length - 4 }}개 더
          </span>
        </div>
      </div>
    </footer>
  </article>
</template>

<style scoped lang="scss">
.news-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  
  &:hover {
    transform: translateY(-4px) translateX(2px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    
    .read-more {
      opacity: 1;
      transform: translateX(0);
    }
    
    .news-title {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 1rem;
  }
}

.category-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border: 1px solid rgba(102, 126, 234, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #667eea;
  flex-shrink: 0;
  transition: all 0.3s ease;
  
  &:hover {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
    transform: translateY(-2px);
  }
}

.category-emoji {
  font-size: 1.1rem;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.category-text {
  font-weight: 700;
}

.meta-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
  
  @media (max-width: 768px) {
    align-items: flex-start;
  }
}

.author, .date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.author-icon, .date-icon {
  font-size: 1rem;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.card-content {
  display: block;
  text-decoration: none;
  color: inherit;
  margin-bottom: 2rem;
  position: relative;
}

.news-title {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1.3;
  margin-bottom: 1rem;
  color: #1a1a1a;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    font-size: 1.25rem;
  }
}

.news-summary {
  font-size: 1rem;
  line-height: 1.6;
  color: #555;
  margin-bottom: 1.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.read-more {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #667eea;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
  
  svg {
    transition: transform 0.2s ease;
  }
  
  &:hover svg {
    transform: translate(2px, -2px);
  }
}

.card-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  padding-top: 1.5rem;
}

.engagement-stats {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.stat-item, .external-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
  text-decoration: none;
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 50px;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    transform: translateY(-1px);
  }
}

.stat-icon {
  font-size: 1rem;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.stat-value {
  font-weight: 600;
  min-width: 20px;
  text-align: center;
}

.keywords {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.keywords-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #667eea;
}

.keywords-icon {
  font-size: 1rem;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.8rem;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
  
  // 4가지 테마 색상
  &.keyword-theme-1 {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    border: 1px solid rgba(102, 126, 234, 0.2);
    color: #667eea;
    
    &:hover {
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
      border-color: rgba(102, 126, 234, 0.4);
    }
  }
  
  &.keyword-theme-2 {
    background: linear-gradient(135deg, rgba(240, 147, 251, 0.1), rgba(245, 87, 108, 0.1));
    border: 1px solid rgba(240, 147, 251, 0.2);
    color: #f093fb;
    
    &:hover {
      background: linear-gradient(135deg, rgba(240, 147, 251, 0.2), rgba(245, 87, 108, 0.2));
      border-color: rgba(240, 147, 251, 0.4);
    }
  }
  
  &.keyword-theme-3 {
    background: linear-gradient(135deg, rgba(74, 222, 128, 0.1), rgba(34, 197, 94, 0.1));
    border: 1px solid rgba(74, 222, 128, 0.2);
    color: #22c55e;
    
    &:hover {
      background: linear-gradient(135deg, rgba(74, 222, 128, 0.2), rgba(34, 197, 94, 0.2));
      border-color: rgba(74, 222, 128, 0.4);
    }
  }
  
  &.keyword-theme-4 {
    background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.1));
    border: 1px solid rgba(251, 191, 36, 0.2);
    color: #f59e0b;
    
    &:hover {
      background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.2));
      border-color: rgba(251, 191, 36, 0.4);
    }
  }
}

.more-tags {
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.8rem;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #999;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(0, 0, 0, 0.1);
    color: #666;
    transform: translateY(-1px);
  }
}

@media (max-width: 768px) {
  .news-card {
    padding: 1.5rem;
  }
  
  .engagement-stats {
    flex-wrap: wrap;
    gap: 0.75rem;
  }
  
  .stat-item, .external-link {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }
}

:deep(mark) {
  background-color: #fff3cd;
  padding: 0 2px;
  border-radius: 2px;
}
</style>
