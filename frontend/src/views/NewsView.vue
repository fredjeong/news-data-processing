<script setup>
import { ref, onMounted, computed, watch } from "vue";
import ContentBox from "@/common/ContentBox.vue";
import NewsCard from "@/components/NewsCard.vue"; // 뉴스 카드 컴포넌트로 fetchNews 데이터 prop
import { tabs } from "@/assets/data/tabs";
import axiosInstance from "@/utils/axios";

const newsList = ref([]);
const sortBy = ref("latest");
const activeTab = ref(tabs[0].id);
const currentPage = ref(1);
const itemsPerPage = 6;
const isLoading = ref(false);

// 서버사이드 페이지네이션 정보
const serverPaginationInfo = ref({
  count: 0,
  totalPages: 0,
  currentPage: 1,
  pageSize: 6,
  hasNext: false,
  hasPrevious: false
});

// 탭 스크롤 관련
const tabsContainer = ref(null);
const showLeftArrow = ref(false);
const showRightArrow = ref(true);

// 데이터 로드 함수
const fetchNews = async () => {
  try {
    isLoading.value = true;
    console.log('Fetching news data...', {
      category: activeTab.value,
      page: currentPage.value
    });
    
    const params = {
      category: activeTab.value,
      page: currentPage.value
    };
    
    const response = await axiosInstance.get("/articles/optimized/", { params });
    console.log('Server response:', response.data);
    
    // 서버에서 받은 페이지네이션된 데이터를 직접 사용
    newsList.value = response.data.results;
    
    // 서버 응답에서 페이지네이션 정보 업데이트
    serverPaginationInfo.value = {
      count: response.data.count,
      totalPages: response.data.total_pages,
      currentPage: response.data.current_page,
      pageSize: response.data.page_size,
      hasNext: !!response.data.next,
      hasPrevious: !!response.data.previous
    };
    
  } catch (error) {
    console.error('Error fetching news:', error);
    newsList.value = [];
    serverPaginationInfo.value = {
      count: 0,
      totalPages: 0,
      currentPage: 1,
      pageSize: 6,
      hasNext: false,
      hasPrevious: false
    };
  } finally {
    isLoading.value = false;
  }
};

// 서버에서 이미 필터링된 뉴스 목록 (기존 UI 호환성을 위해 유지)
const filteredNews = computed(() => {
  // 서버사이드 페이지네이션에서는 전체 개수만 필요
  return {
    length: serverPaginationInfo.value.count || 0
  };
});

// 서버에서 이미 페이지네이션된 뉴스 목록 (기존 UI 호환성을 위해 유지)
const paginatedNews = computed(() => {
  // 서버에서 받은 데이터를 그대로 반환
  return newsList.value;
});

// 서버에서 받은 전체 페이지 수
const totalPages = computed(() => {
  return serverPaginationInfo.value.totalPages || 0;
});

// 스마트 페이지네이션 - 표시할 페이지 번호들 계산
const visiblePages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  const maxVisible = 5; // 최대 표시할 페이지 수
  
  if (total <= maxVisible) {
    // 전체 페이지가 5개 이하면 모두 표시
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  
  let start = Math.max(1, current - Math.floor(maxVisible / 2));
  let end = Math.min(total, start + maxVisible - 1);
  
  // 끝에서 시작점 조정
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1);
  }
  
  const pages = [];
  
  // 첫 페이지 추가
  if (start > 1) {
    pages.push(1);
    if (start > 2) {
      pages.push('...');
    }
  }
  
  // 중간 페이지들 추가
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  
  // 마지막 페이지 추가
  if (end < total) {
    if (end < total - 1) {
      pages.push('...');
    }
    pages.push(total);
  }
  
  return pages;
});

// 페이지 변경 함수
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
    currentPage.value = page;
    fetchNews();
    
    // news-content 요소보다 약간 위로 스크롤
    const newsContent = document.querySelector('.news-content');
    if (newsContent) {
      const offset = 100; // 상단 여백 조정값
      const elementPosition = newsContent.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;
      
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  }
};

// 다음 페이지로
const nextPage = () => {
  if (serverPaginationInfo.value.hasNext) {
    changePage(currentPage.value + 1);
  }
};

// 이전 페이지로
const previousPage = () => {
  if (serverPaginationInfo.value.hasPrevious) {
    changePage(currentPage.value - 1);
  }
};

// 첫 페이지로
const goToFirstPage = () => {
  changePage(1);
};

// 마지막 페이지로
const goToLastPage = () => {
  changePage(totalPages.value);
};

// 카테고리 변경 시 페이지 초기화 및 데이터 재로드
watch(activeTab, () => {
  currentPage.value = 1;
  fetchNews();
});

// 정렬 변경 시 페이지 초기화 및 데이터 재로드
watch(sortBy, () => {
  currentPage.value = 1;
  fetchNews();
});

const getActiveTabLabel = () => {
  const selectedTab = tabs.find(tab => tab.id === activeTab.value);
  return selectedTab ? selectedTab.label : '전체';
};

const getActiveTabEmoji = () => {
  const selectedTab = tabs.find(tab => tab.id === activeTab.value);
  return selectedTab ? selectedTab.emoji : '📰';
};

// 스크롤 상태 업데이트 (화살표 비활성화 상태 관리용)
const updateScrollState = () => {
  const container = tabsContainer.value;
  if (!container) return;
  
  showLeftArrow.value = container.scrollLeft > 0;
  showRightArrow.value = container.scrollLeft < container.scrollWidth - container.clientWidth;
};

// 컴포넌트 마운트 후 스크롤 상태 초기화
onMounted(() => {
  fetchNews();
  setTimeout(() => {
    updateScrollState();
  }, 100);
});
</script>

<template>
  <div class="news-container">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-icon">✨</span>
          <span>AI 기반 뉴스 큐레이션</span>
        </div>
        <h1 class="hero-title">
          <span class="title-gradient">당신만을 위한</span>
          <br>
          <span class="title-highlight">맞춤형 뉴스</span>
        </h1>
        <p class="hero-description">
          AI가 분석한 당신의 관심사를 바탕으로<br>
          <strong>개인화된 뉴스</strong>를 실시간으로 큐레이션합니다
        </p>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">{{ filteredNews.length }}+</span>
            <span class="stat-label">큐레이션된 뉴스</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">18</span>
            <span class="stat-label">카테고리</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">24/7</span>
            <span class="stat-label">실시간 업데이트</span>
          </div>
        </div>
      </div>
      <div class="hero-visual">
        <div class="floating-cards">
          <div class="floating-card card-1">📰</div>
          <div class="floating-card card-2">🤖</div>
          <div class="floating-card card-3">📊</div>
          <div class="floating-card card-4">🎯</div>
        </div>
      </div>
    </div>

    <!-- Category Tabs -->
    <div class="category-section">
      <div class="section-header">
        <h2 class="section-title">
          <span class="title-icon">🎯</span>
          관심 카테고리 선택
        </h2>
        <p class="section-subtitle">원하는 분야의 뉴스를 골라보세요</p>
      </div>
      
      <div class="tabs-container">
        <div class="tabs-wrapper">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="category-tab"
            :class="{ 'category-tab--active': activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <span class="tab-emoji">{{ tab.emoji }}</span>
            <span class="tab-label">{{ tab.label }}</span>
            <div class="tab-glow"></div>
          </button>
        </div>
      </div>
    </div>

    <!-- News Content -->
    <div class="content-section">
      <ContentBox class="news-content">
        <div class="content-header">
          <div class="content-info">
            <h3 class="content-title">
              <span class="content-icon">{{ getActiveTabEmoji() }}</span>
              {{ getActiveTabLabel() }} 뉴스
            </h3>
            <p class="content-subtitle">
              총 {{ filteredNews.length }}개의 뉴스가 있습니다
            </p>
          </div>
          <div class="content-controls">
            <div class="sort-container">
              <label class="sort-label">정렬</label>
              <select class="sort-select" v-model="sortBy">
                <option value="latest">🕒 최신순</option>
                <option value="likes">❤️ 좋아요순</option>
                <option value="views">👀 조회수순</option>
              </select>
            </div>
          </div>
        </div>

        <div class="news-grid" v-if="!isLoading && paginatedNews.length > 0">
          <NewsCard 
            v-for="(news, index) in paginatedNews" 
            :key="news.id" 
            :article="news"
            :style="{ animationDelay: `${index * 0.1}s` }"
            class="news-item"
          />
        </div>

        <div v-else-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p class="loading-text">AI가 뉴스를 분석하고 있습니다...</p>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">📭</div>
          <h3 class="empty-title">해당 카테고리에 뉴스가 없습니다</h3>
          <p class="empty-description">다른 카테고리를 선택해보세요</p>
        </div>

                 <div class="pagination-container" v-if="totalPages > 1">
          <button 
            class="pagination-button prev" 
            :disabled="!serverPaginationInfo.hasPrevious"
            @click="previousPage"
          >
            <span class="button-icon">←</span>
            <span class="button-text">이전</span>
          </button>
          
          <div class="page-numbers">
            <button 
              v-for="page in visiblePages" 
              :key="page"
              class="page-number"
              :class="{ 
                'active': currentPage === page,
                'ellipsis': page === '...'
              }"
              :disabled="page === '...'"
              @click="page !== '...' && changePage(page)"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            class="pagination-button next" 
            :disabled="!serverPaginationInfo.hasNext"
            @click="nextPage"
          >
            <span class="button-text">다음</span>
            <span class="button-icon">→</span>
          </button>
        </div>
      </ContentBox>
    </div>
  </div>
</template>

<style scoped lang="scss">
.news-container {
  min-height: 100vh;
  padding-bottom: 4rem;
}

// Hero Section
.hero-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  margin-bottom: 6rem;
  padding: 4rem 0;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }
}

.hero-content {
  animation: fadeInUp 0.8s ease-out;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.badge-icon {
  font-size: 1.2rem;
  animation: pulse 2s infinite;
}

.hero-title {
  font-size: 4rem;
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
}

.title-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-highlight {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border-radius: 2px;
    opacity: 0.3;
  }
}

.hero-description {
  font-size: 1.25rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 3rem;
  
  strong {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
  }
}

.hero-stats {
  display: flex;
  gap: 2rem;
  
  @media (max-width: 768px) {
    justify-content: center;
  }
}

.stat-item {
  text-align: center;
  
  .stat-number {
    display: block;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
  }
  
  .stat-label {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
    font-weight: 500;
  }
}

.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  animation: slideInRight 0.8s ease-out 0.2s both;
}

.floating-cards {
  position: relative;
  width: 300px;
  height: 300px;
}

.floating-card {
  position: absolute;
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  &.card-1 {
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    animation: float 3s ease-in-out infinite;
  }
  
  &.card-2 {
    top: 50%;
    right: 0;
    transform: translateY(-50%);
    animation: float 3s ease-in-out infinite 0.5s;
  }
  
  &.card-3 {
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    animation: float 3s ease-in-out infinite 1s;
  }
  
  &.card-4 {
    top: 50%;
    left: 0;
    transform: translateY(-50%);
    animation: float 3s ease-in-out infinite 1.5s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(-50%);
  }
  50% {
    transform: translateY(-20px) translateX(-50%);
  }
}

// Category Section
.category-section {
  margin-bottom: 4rem;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
}

.title-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
}

.section-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.tabs-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.tabs-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  max-height: 400px;
  overflow-y: auto;
  padding: 1rem;
}

.category-tab {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem 1rem;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
  backdrop-filter: blur(10px);
  overflow: hidden;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    border-color: rgba(102, 126, 234, 0.3);
    
    .tab-glow {
      opacity: 0.5;
      transform: scale(1.1);
    }
  }
  
  &--active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    
    .tab-glow {
      opacity: 1;
    }
    
    .tab-emoji {
      animation: pulse 1s infinite;
    }
  }
}

.tab-glow {
  position: absolute;
  inset: -2px;
  background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
  border-radius: 18px;
  opacity: 0;
  z-index: -1;
  filter: blur(8px);
  transition: all 0.3s ease;
}

.tab-emoji {
  font-size: 2rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.tab-label {
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
}

// Content Section
.content-section {
  animation: fadeInUp 0.8s ease-out 0.4s both;
}

.news-content {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 24px !important;
  padding: 3rem !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 3rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 1rem;
  }
}

.content-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.content-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.5));
  opacity: 1;
  display: inline-block;
  color: #667eea;
  -webkit-text-fill-color: #667eea;
}

.content-subtitle {
  color: #666;
  font-size: 1.1rem;
  font-weight: 500;
}

.sort-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.8);
  padding: 1rem 1.5rem;
  border-radius: 50px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.sort-label {
  font-weight: 600;
  color: #667eea;
  font-size: 0.9rem;
}

.sort-select {
  border: none;
  background: transparent;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
  }
  
  &:focus {
    outline: none;
    background: rgba(102, 126, 234, 0.1);
  }
  
  option {
    font-weight: 600;
    padding: 0.5rem;
  }
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.news-item {
  animation: fadeInUp 0.6s ease-out both;
}

// Loading State
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(102, 126, 234, 0.1);
  border-left: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 2rem;
}

.loading-text {
  font-size: 1.2rem;
  color: #667eea;
  font-weight: 600;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// Empty State
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 1rem;
}

.empty-description {
  font-size: 1.1rem;
  color: #666;
}

// Pagination
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 3rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.pagination-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    background: rgba(102, 126, 234, 0.2);
    transform: translateY(-2px);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .button-icon {
    font-size: 1.2rem;
  }
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.page-number {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: #666;
  font-weight: 600;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(.active) {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
  }
  
  &.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  
  &.ellipsis {
    cursor: default;
    color: #999;
    
    &:hover {
      background: transparent;
      color: #999;
    }
  }
}

@media (max-width: 768px) {
  .pagination-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .page-numbers {
    order: -1;
  }
}

// Animations
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

// Responsive Design
@media (max-width: 1024px) {
  .hero-section {
    padding: 2rem 0;
    margin-bottom: 4rem;
  }
  
  .hero-title {
    font-size: 3rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .hero-stats {
    flex-direction: column;
    gap: 1rem;
  }
  
  .tabs-wrapper {
    padding: 0.5rem;
  }
  
  .category-tab {
    min-width: 100px;
    padding: 1rem 0.5rem;
  }
  
  .content-header {
    text-align: center;
  }
  
  .sort-container {
    justify-content: center;
  }
}
</style>
