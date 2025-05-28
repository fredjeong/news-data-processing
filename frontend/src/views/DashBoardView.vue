<script setup>
import { Bar, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import { ref, onMounted } from "vue";
import ArticlePreview from "@/components/ArticlePreview.vue";
import UserRecommendations from "@/components/UserRecommendations.vue";
import axiosInstance from "@/utils/axios";

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

// 로딩 상태 관리
const isLoading = ref({
  stats: true,
  keywords: true,
  weeklyReads: true,
  scraps: true
});

// 사용자 통계
const userStats = ref({
  totalArticles: 0,
  totalLikes: 0,
  favoriteCategories: [],
  totalScraps: 0
});

// 카테고리 차트 데이터
const categoryData = ref({
  labels: [],
  datasets: [
    {
      data: [],
      backgroundColor: [],
    },
  ],
});
const categories = ref([]);

// 스크랩한 기사 목록
const scrapedArticles = ref([]);

// 키워드 차트 데이터
const keywordData = ref({
  labels: [],
  datasets: [
    {
      label: "키워드 빈도수",
      data: [],
      backgroundColor: [],
      borderColor: [],
      borderWidth: 2,
      borderRadius: 8,
      borderSkipped: false,
    },
  ],
});

// 주간 읽은 기사 데이터
const readData = ref({
  labels: generateDateLabels(),
  datasets: [
    {
      label: "읽은 기사 수",
      data: [0, 0, 0, 0, 0, 0, 0],
      backgroundColor: "#DBB8E4",
    },
  ],
});

// 주간 비교 데이터를 저장할 ref 추가
const weeklyComparison = ref({
  view: 0,
  like: 0,
  scrap: 0
});

// 차트 옵션
const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "bottom",
      labels: {
        padding: 12,
        boxWidth: 16,
        font: {
          size: 12,
        },
        usePointStyle: true,
        generateLabels: function(chart) {
          const data = chart.data;
          if (data.labels.length && data.datasets.length) {
            return data.labels.map((label, i) => {
              const value = data.datasets[0].data[i];
              return {
                text: `${label} (${value}개)`,
                fillStyle: data.datasets[0].backgroundColor[i],
                strokeStyle: data.datasets[0].backgroundColor[i],
                lineWidth: 0,
                pointStyle: 'circle',
                hidden: false,
                index: i
              };
            });
          }
          return [];
        }
      },
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const label = context.label || "";
          const value = context.raw;
          const total = context.dataset.data.reduce((a, b) => a + b, 0);
          const percentage = ((value / total) * 100).toFixed(1);
          return `${label}: ${value}개 (${percentage}%)`;
        },
      },
    },
  },
};

const barOptions = {
  indexAxis: "x",
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index',
  },
  animation: {
    duration: 1000,
    easing: 'easeInOutQuart',
  },
  scales: {
    x: {
      beginAtZero: true,
      grid: {
        display: false,
      },
      ticks: {
        maxRotation: 45,
        minRotation: 45,
        font: {
          size: 12,
          weight: '600',
        },
        color: '#666',
      },
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
        lineWidth: 1,
      },
      ticks: {
        precision: 0,
        stepSize: 1,
        font: {
          size: 12,
          weight: '600',
        },
        color: '#666',
        callback: function(value) {
          return Number.isInteger(value) ? value + '회' : '';
        }
      }
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: 'rgba(102, 126, 234, 0.5)',
      borderWidth: 1,
      cornerRadius: 8,
      displayColors: true,
      callbacks: {
        title: (context) => {
          return `키워드: ${context[0].label}`;
        },
        label: (context) => {
          const value = context.raw;
          return `등장 횟수: ${value}회`;
        },
      },
    },
  },
  onHover: (event, activeElements) => {
    event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
  },
};

const readBarOptions = {
  indexAxis: "x",
  scales: {
    x: {
      beginAtZero: true,
    },
    y: {
      beginAtZero: true,
      ticks: {
        precision: 0,
        stepSize: 1,
        callback: function(value) {
          return Number.isInteger(value) ? value : '';
        }
      }
    }
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const label = context.label || "";
          const value = context.raw;
          return `${label}: ${value}개`;
        },
      },
    },
  },
};

// 날짜 레이블 생성 함수
function generateDateLabels() {
  const labels = [];
  const today = new Date();
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    // MM-DD 형식으로 포맷팅
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    labels.push(`${month}-${day}`);
  }
  
  return labels;
}

// 대시보드 통계 정보 가져오기
const fetchDashboardStats = async () => {
  try {
    isLoading.value.stats = true;
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('로그인이 필요합니다.');
      return;
    }

    const response = await axiosInstance.get('/accounts/dashboard/stats/');

    userStats.value = {
      totalArticles: response.data.total_articles,
      totalLikes: response.data.total_likes,
      totalScraps: response.data.total_scraps
    };

    // 카테고리 데이터 처리
    const categoryList = response.data.favorite_categories || [];
    const colors = [
      '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
      '#9966FF', '#FF9F40', '#C9CBCF', '#7BC043',
      '#E91E63', '#00BCD4'
    ];

    // 카테고리 목록 생성
    const categoryItems = categoryList.map(cat => [cat.category, cat.count]);
    categories.value = categoryItems;

    // 차트 데이터 설정
    categoryData.value.labels = categoryItems.map(item => item[0]);
    categoryData.value.datasets[0].data = categoryItems.map(item => item[1]);
    categoryData.value.datasets[0].backgroundColor = colors.slice(0, categoryItems.length);

  } catch (error) {
    console.error('대시보드 통계 정보 가져오기 실패:', error);
  } finally {
    isLoading.value.stats = false;
  }
};

// 키워드 빈도 데이터 가져오기
const fetchKeywordData = async () => {
  try {
    isLoading.value.keywords = true;
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const response = await axiosInstance.get('/accounts/dashboard/keywords/');

    const keywordList = response.data || [];
    
    // 키워드별 그라데이션 색상 생성
    const gradientColors = [
      'rgba(102, 126, 234, 0.8)',
      'rgba(118, 75, 162, 0.8)',
      'rgba(240, 147, 251, 0.8)',
      'rgba(245, 87, 108, 0.8)',
      'rgba(74, 222, 128, 0.8)',
      'rgba(34, 197, 94, 0.8)',
      'rgba(251, 191, 36, 0.8)',
      'rgba(245, 158, 11, 0.8)',
      'rgba(59, 130, 246, 0.8)',
      'rgba(147, 51, 234, 0.8)',
    ];
    
    const borderColors = [
      'rgba(102, 126, 234, 1)',
      'rgba(118, 75, 162, 1)',
      'rgba(240, 147, 251, 1)',
      'rgba(245, 87, 108, 1)',
      'rgba(74, 222, 128, 1)',
      'rgba(34, 197, 94, 1)',
      'rgba(251, 191, 36, 1)',
      'rgba(245, 158, 11, 1)',
      'rgba(59, 130, 246, 1)',
      'rgba(147, 51, 234, 1)',
    ];
    
    keywordData.value.labels = keywordList.map(item => item.keyword);
    keywordData.value.datasets[0].data = keywordList.map(item => item.count);
    keywordData.value.datasets[0].backgroundColor = keywordList.map((_, index) => 
      gradientColors[index % gradientColors.length]
    );
    keywordData.value.datasets[0].borderColor = keywordList.map((_, index) => 
      borderColors[index % borderColors.length]
    );
  } catch (error) {
    console.error('키워드 빈도 데이터 가져오기 실패:', error);
  } finally {
    isLoading.value.keywords = false;
  }
};

// 주간 읽은 기사 데이터 가져오기
const fetchWeeklyReads = async () => {
  try {
    isLoading.value.weeklyReads = true;
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const response = await axiosInstance.get('/accounts/dashboard/weekly-reads/');

    // 데이터 업데이트 시 레이블도 함께 업데이트
    readData.value.labels = generateDateLabels();
    readData.value.datasets[0].data = response.data || [0, 0, 0, 0, 0, 0, 0];
  } catch (error) {
    console.error('주간 읽은 기사 데이터 가져오기 실패:', error);
  } finally {
    isLoading.value.weeklyReads = false;
  }
};

// 스크랩한 기사 목록 가져오기
const fetchScrapedArticles = async () => {
  try {
    isLoading.value.scraps = true;
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const response = await axiosInstance.get('/accounts/dashboard/scraps/');
    scrapedArticles.value = response.data || [];
  } catch (error) {
    console.error('스크랩한 기사 목록 가져오기 실패:', error);
  } finally {
    isLoading.value.scraps = false;
  }
};

// 주간 비교 데이터 가져오기 함수
const fetchWeeklyComparison = async () => {
  try {
    const userId = JSON.parse(localStorage.getItem('user')).id;
    const response = await axiosInstance.get(`/accounts/${userId}/weekly-stats/`);
    weeklyComparison.value = {
      view: Math.round(response.data.view.percent_change),
      like: Math.round(response.data.like.percent_change),
      scrap: Math.round(response.data.scrap.percent_change),
    };
  } catch (error) {
    console.error('주간 통계 비교 데이터 가져오기 실패:', error);
    weeklyComparison.value = { view: 0, like: 0, scrap: 0 };
  }
};

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  fetchDashboardStats();
  fetchKeywordData();
  fetchWeeklyReads();
  fetchScrapedArticles();
  fetchWeeklyComparison(); // 주간 비교 데이터 가져오기 추가
});

// 추가 유틸리티 메서드들
const getMostActiveDay = () => {
  if (!readData.value.datasets[0].data.length) return '데이터 없음';
  
  const data = readData.value.datasets[0].data;
  const labels = readData.value.labels;
  const maxIndex = data.indexOf(Math.max(...data));
  
  return labels[maxIndex] || '데이터 없음';
};

const getAverageReads = () => {
  if (!readData.value.datasets[0].data.length) return 0;
  
  const data = readData.value.datasets[0].data;
  const sum = data.reduce((acc, val) => acc + val, 0);
  
  return Math.round(sum / data.length * 10) / 10;
};

const getRecommendationAccuracy = () => {
  // 읽은 기사 수와 좋아요 수를 기반으로 추천 정확도 계산
  const articles = userStats.value.totalArticles;
  const likes = userStats.value.totalLikes;
  
  if (articles === 0) return 0;
  
  // 기본 정확도 + 활동량에 따른 보너스
  const baseAccuracy = 60;
  const activityBonus = Math.min(30, (articles + likes) * 2);
  const engagementBonus = articles > 0 ? Math.min(10, (likes / articles) * 100) : 0;
  
  return Math.round(baseAccuracy + activityBonus + engagementBonus);
};

const getWeeklyComparison = () => {
  return weeklyComparison.value;
};

const getMostReadCategory = () => {
  if (!categories.value.length) return '아직 없음';
  
  return categories.value[0][0];
};
</script>

<template>
  <div class="dashboard">
     <!-- Hero Section -->
     <div class="dashboard-hero">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-icon">📊</span>
          <span>개인화된 뉴스 분석</span>
        </div>
        <h1 class="hero-title">
          <span class="title-gradient">나만의</span>
          <span class="title-highlight">뉴스 대시보드</span>
        </h1>
        <p class="hero-description">
          AI가 분석한 당신의 뉴스 소비 패턴과<br>
          <strong>개인화된 인사이트</strong>를 한눈에 확인하세요
        </p>
      </div>
      <div class="hero-visual">
        <div class="floating-stats">
          <div class="floating-stat stat-1">
            <span class="stat-icon">📚</span>
            <span class="stat-value">{{ userStats.totalArticles }}</span>
            <span class="stat-label">읽은 기사</span>
          </div>
          <div class="floating-stat stat-2">
            <span class="stat-icon">❤️</span>
            <span class="stat-value">{{ userStats.totalLikes }}</span>
            <span class="stat-label">좋아요</span>
          </div>
          <div class="floating-stat stat-3">
            <span class="stat-icon">🎯</span>
            <span class="stat-value">{{ categories.length }}</span>
            <span class="stat-label">관심 분야</span>
          </div>
        </div>
      </div>
    </div>

    <div class="dashboard-layout">
      <!-- 메인 콘텐츠 영역 -->
      <div class="main-content">
        <!-- 통계 정보 카드 -->
        <div class="stats-overview">
          <div class="stats-grid">
            <div class="stat-card primary">
              <div class="stat-icon-wrapper">
                <span class="stat-icon">📚</span>
              </div>
              <div class="stat-content">
                <h3>총 읽은 기사</h3>
                <p class="stat-number">{{ userStats.totalArticles }}</p>
                <span class="stat-trend" :class="{ 'negative': getWeeklyComparison().view < 0 }">
                  지난주 대비 {{ getWeeklyComparison().view > 0 ? '+' : '' }}{{ getWeeklyComparison().view }}%
                </span>
              </div>
              <div class="stat-glow"></div>
            </div>
            
            <div class="stat-card secondary">
              <div class="stat-icon-wrapper">
                <span class="stat-icon">❤️</span>
              </div>
              <div class="stat-content">
                <h3>총 좋아요</h3>
                <p class="stat-number">{{ userStats.totalLikes }}</p>
                <span class="stat-trend" :class="{ 'negative': getWeeklyComparison().like < 0 }">
                  지난주 대비 {{ getWeeklyComparison().like > 0 ? '+' : '' }}{{ getWeeklyComparison().like }}%
                </span>
              </div>
              <div class="stat-glow"></div>
            </div>

            <div class="stat-card tertiary">
              <div class="stat-icon-wrapper">
                <span class="stat-icon">📑</span>
              </div>
              <div class="stat-content">
                <h3>스크랩한 기사</h3>
                <p class="stat-number">{{ userStats.totalScraps }}</p>
                <span class="stat-trend">좋습니다!</span>
              </div>
              <div class="stat-glow"></div>
            </div>
            
            <div class="stat-card quaternary">
              <div class="stat-icon-wrapper">
                <span class="stat-icon">📈</span>
              </div>
              <div class="stat-content">
                <h3>활동 점수</h3>
                <p class="stat-number">{{ Math.round(userStats.totalArticles + userStats.totalLikes * 1.5 + userStats.totalScraps * 2) }}</p>
                <span class="stat-trend">매우 활발</span>
              </div>
              <div class="stat-glow"></div>
            </div>
          </div>
        </div>

        <!-- AI 맞춤 추천 섹션 -->
        <div class="recommendations-section">
          <div class="recommendations-card">
            <div class="recommendations-header">
              <div class="recommendations-title">
                <span class="recommendations-icon">🤖</span>
                <h2>AI 맞춤 추천</h2>
              </div>
              <p class="recommendations-description">
                당신의 관심사를 분석하여 <strong>개인화된 뉴스</strong>를 추천합니다
              </p>
              <div class="ai-badge">
                <span class="ai-icon">✨</span>
                <span>AI 분석 완료</span>
              </div>
            </div>
            
            <div class="recommendations-content">
              <UserRecommendations />
            </div>
            
            <div class="recommendations-footer">
              <div class="accuracy-indicator">
                <span class="accuracy-label">추천 정확도</span>
                <div class="accuracy-bar">
                  <div class="accuracy-progress" :style="{ width: `${getRecommendationAccuracy()}%` }"></div>
                </div>
                <span class="accuracy-value">{{ getRecommendationAccuracy() }}%</span>
              </div>
              <p class="accuracy-tip">
                더 많은 기사를 읽고 좋아요를 누를수록 정확도가 향상됩니다
              </p>
            </div>
          </div>
        </div>

        <!-- 차트 섹션 -->
        <div class="charts-section">
          <div class="chart-card category-chart">
            <div class="chart-header">
              <div class="chart-title">
                <span class="chart-icon">🎯</span>
                <h2>관심 카테고리 분석</h2>
              </div>
              <p class="chart-description">
                AI가 분석한 당신의 뉴스 소비 패턴을 통해 가장 관심 있는 카테고리를 시각화합니다
              </p>
            </div>
            
            <div class="chart-content">
              <div v-if="!isLoading.stats && categories.length > 0" class="category-visualization">
                <div class="chart-wrapper">
                  <Doughnut :data="categoryData" :options="options" />
                </div>
                <div class="category-insights">
                  <h4>📊 카테고리 순위</h4>
                  <div class="category-list">
                    <div
                      v-for="(category, index) in categories.slice(0, 5)"
                      :key="index"
                      class="category-item"
                      :style="{
                        '--category-color': categoryData.datasets[0].backgroundColor[index],
                      }"
                    >
                      <div class="category-rank">{{ index + 1 }}</div>
                      <div class="category-info">
                        <span class="category-name">{{ category[0] }}</span>
                        <span class="category-count">{{ category[1] }}개 기사</span>
                      </div>
                      <div class="category-bar">
                        <div 
                          class="category-progress" 
                          :style="{ width: `${(category[1] / categories[0][1]) * 100}%` }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else-if="isLoading.stats" class="loading-state">
                <div class="loading-spinner"></div>
                <p>AI가 데이터를 분석하고 있습니다...</p>
              </div>
              <div v-else class="empty-state">
                <div class="empty-icon">📊</div>
                <h3>아직 분석할 데이터가 없습니다</h3>
                <p>더 많은 기사를 읽어보세요!</p>
              </div>
            </div>
          </div>
          
          <div class="chart-card keyword-chart">
            <div class="chart-header">
              <div class="chart-title">
                <span class="chart-icon">🏷️</span>
                <h2>핵심 키워드 분석</h2>
              </div>
              <p class="chart-description">
                읽은 기사들에서 추출한 핵심 키워드를 빈도수별로 분석하여 관심사를 파악합니다
              </p>
            </div>
            
            <div class="chart-content">
              <div v-if="!isLoading.keywords && keywordData.labels.length > 0" class="keyword-visualization">
                <div class="chart-wrapper">
                  <Bar :data="keywordData" :options="barOptions" />
                </div>
                <div class="keyword-insights">
                  <div class="insights-header">
                    <span class="insights-icon">🏷️</span>
                    <h4>주요 키워드</h4>
                  </div>
                  <div class="keyword-tags">
                    <span
                      v-for="(keyword, index) in keywordData.labels.slice(0, 8)"
                      :key="index"
                      class="keyword-tag"
                      :class="`keyword-theme-${(index % 4) + 1}`"
                    >
                      #{{ keyword }}
                    </span>
                  </div>
                  <div class="keyword-summary">
                    <p>총 <strong>{{ keywordData.labels.length }}개</strong>의 키워드를 분석했습니다</p>
                  </div>
                </div>
              </div>
              <div v-else-if="isLoading.keywords" class="loading-state">
                <div class="loading-spinner"></div>
                <p>키워드를 분석하고 있습니다...</p>
              </div>
              <div v-else class="empty-state">
                <div class="empty-icon">🔍</div>
                <h3>키워드 데이터가 없습니다</h3>
                <p>더 많은 기사를 읽어보세요!</p>
              </div>
            </div>
          </div>
        </div>

         <!-- 활동 분석 섹션 -->
         <div class="activity-section">
          <div class="chart-card weekly-chart">
            <div class="chart-header">
              <div class="chart-title">
                <span class="chart-icon">📈</span>
                <h2>주간 활동 분석</h2>
              </div>
              <p class="chart-description">
                최근 7일간의 뉴스 소비 패턴을 분석하여 당신의 읽기 습관을 시각화합니다
              </p>
            </div>
            <div class="chart-content">
              <div v-if="!isLoading.weeklyReads" class="weekly-visualization">
                <div class="chart-wrapper">
                  <Bar :data="readData" :options="readBarOptions" />
                </div>
                <div class="weekly-insights">
                  <div class="insight-item">
                    <span class="insight-icon">🔥</span>
                    <div class="insight-content">
                      <span class="insight-label">가장 활발한 날</span>
                      <span class="insight-value">{{ getMostActiveDay() }}</span>
                    </div>
                  </div>
                  <div class="insight-item">
                    <span class="insight-icon">📊</span>
                    <div class="insight-content">
                      <span class="insight-label">일평균 읽기</span>
                      <span class="insight-value">{{ getAverageReads() }}개</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="loading-state">
                <div class="loading-spinner"></div>
                <p>활동 데이터를 분석하고 있습니다...</p>
              </div>
            </div>
          
          </div>

          <div class="chart-card favorites-card">
            <div class="chart-header">
              <div class="chart-title">
                <span class="chart-icon">📑</span>
                <h2>스크랩한 기사</h2>
              </div>
              <p class="chart-description">
                나중에 다시 보고 싶은 기사들을 모아보세요
              </p>
            </div>
            <div class="chart-content favorites-content">
              <div v-if="!isLoading.scraps && scrapedArticles.length > 0" class="favorites-list">
                <div 
                  v-for="article in scrapedArticles.slice(0, 5)" 
                  :key="article.id"
                  class="favorite-item"
                >
                  <ArticlePreview :to="`/news/${article.id}`" :news="article" />
                </div>
                <div v-if="scrapedArticles.length > 5" class="view-more">
                  <button class="view-more-btn">
                    <span>더 보기</span>
                    <span class="more-count">+{{ scrapedArticles.length - 5 }}</span>
                  </button>
                </div>
              </div>
              <div v-else-if="isLoading.scraps" class="loading-state">
                <div class="loading-spinner"></div>
                <p>스크랩한 기사를 불러오고 있습니다...</p>
              </div>
              <div v-else class="empty-state">
                <div class="empty-icon">📑</div>
                <h3>아직 스크랩한 기사가 없습니다</h3>
                <p>마음에 드는 기사를 스크랩해보세요!</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 오른쪽 사이드바 -->
      <div class="sidebar">

      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard {
  min-height: 100vh;
  padding-bottom: 4rem;
}

// Hero Section
.dashboard-hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  margin-bottom: 4rem;
  padding: 2rem 0;
  
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
  font-size: 3.5rem;
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
  margin-right: 1rem;
}

.title-highlight {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.25rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  
  strong {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
  }
}

.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  animation: slideInRight 0.8s ease-out 0.2s both;
}

.floating-stats {
  position: relative;
  width: 300px;
  height: 300px;
}

.floating-stat {
  position: absolute;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-width: 100px;
  
  &.stat-1 {
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    animation: float 3s ease-in-out infinite;
  }
  
  &.stat-2 {
    top: 50%;
    right: 50%;
    transform: translateY(-50%);
    animation: float 3s ease-in-out infinite 0.5s;
  }
  
  &.stat-3 {
    bottom: 0;
    left: 60%;
    transform: translateX(-50%);
    animation: float 3s ease-in-out infinite 1s;
  }
  
  .stat-icon {
    font-size: 2rem;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  }
  
  .stat-value {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .stat-label {
    font-size: 0.8rem;
    color: #666;
    font-weight: 600;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(-50%);
  }
  50% {
    transform: translateY(-10px) translateX(-50%);
  }
}

// Layout
.dashboard-layout {
  display: flex;
  gap: 2rem;
  
  @media (max-width: 1024px) {
    flex-direction: column;
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3rem;
}


// Stats Overview
.stats-overview {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  
  @media (max-width: 1200px) {
  grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 32px 64px rgba(0, 0, 0, 0.15);
    
    .stat-glow {
      opacity: 1;
    }
  }
  
  &.primary .stat-glow {
    background: linear-gradient(45deg, #667eea, #764ba2);
  }
  
  &.secondary .stat-glow {
    background: linear-gradient(45deg, #f093fb, #f5576c);
  }
  
  &.tertiary .stat-glow {
    background: linear-gradient(45deg, #4facfe, #00f2fe);
  }
  
  &.quaternary .stat-glow {
    background: linear-gradient(45deg, #43e97b, #38f9d7);
  }
}

.stat-glow {
  position: absolute;
  inset: -2px;
  border-radius: 22px;
  opacity: 0;
  z-index: -1;
  filter: blur(8px);
  transition: opacity 0.3s ease;
}

.stat-icon-wrapper {
  margin-bottom: 1rem;
  
  .stat-icon {
    font-size: 2.5rem;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
  }
}

.stat-content {
  h3 {
    font-size: 0.9rem;
    font-weight: 600;
    color: #666;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .stat-number {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
  }
  
  .stat-trend {
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    
    &.negative {
      color: #ef4444;
      background: rgba(239, 68, 68, 0.1);
    }
    
    &:not(.negative) {
      color: #22c55e;
      background: rgba(34, 197, 94, 0.1);
    }
  }
}

// Chart Sections
.charts-section, .activity-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 32px 64px rgba(0, 0, 0, 0.15);
  }
}

.chart-header {
  margin-bottom: 2rem;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  
  .chart-icon {
    font-size: 1.5rem;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  }
  
  h2 {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.chart-description {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
}

.chart-content {
  min-height: 400px;
}

.chart-wrapper {
  height: 350px;
  margin-bottom: 2rem;
}

// Category Insights
.category-insights, .keyword-insights, .weekly-insights {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 16px;
  padding: 1.5rem;
  
  h4 {
    font-size: 1rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.category-rank {
  width: 24px;
  height: 24px;
  background: var(--category-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.category-info {
  flex: 1;
  
  .category-name {
    display: block;
    font-weight: 600;
    color: #333;
    margin-bottom: 0.25rem;
  }
  
  .category-count {
    font-size: 0.8rem;
  color: #666;
  }
}

.category-bar {
  width: 60px;
  height: 4px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.category-progress {
  height: 100%;
  background: var(--category-color);
  border-radius: 2px;
  transition: width 0.3s ease;
}

// Keyword Section
.keyword-insights {
  .insights-header {
  display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    
    .insights-icon {
      font-size: 1.2rem;
      filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }
    
    h4 {
      font-size: 1.1rem;
      font-weight: 700;
      color: #333;
      margin: 0;
    }
  }
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
  
  // 4가지 테마 색상 (NewsCard와 동일)
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

.keyword-summary {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border-left: 4px solid #667eea;
  
  p {
    margin: 0;
    font-size: 0.9rem;
    color: #555;
    
    strong {
      color: #667eea;
      font-weight: 700;
    }
  }
}

// Weekly Insights
.weekly-insights {
  display: flex;
  gap: 1rem;

  @media (max-width: 768px) {
    flex-direction: column;
  }
}

.insight-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.insight-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.insight-content {
  .insight-label {
    display: block;
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 0.25rem;
  }
  
  .insight-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: #333;
  }
}

// Favorites
.favorites-content {
  min-height: 500px;
}

.favorites-list {
    display: flex;
    flex-direction: column;
  gap: 1rem;
}

.favorite-item {
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateX(4px);
  }
}

.view-more {
  margin-top: 1rem;
  text-align: center;
}

.view-more-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
    align-items: center;
  gap: 0.5rem;
  margin: 0 auto;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  .more-count {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.25rem 0.5rem;
    border-radius: 50px;
    font-size: 0.8rem;
  }
}

// Recommendations Section (in main content)
.recommendations-section {
  margin-bottom: 2rem;
  
  .recommendations-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 32px 64px rgba(0, 0, 0, 0.15);
    }
    
    .recommendations-content {
      // UserRecommendations 컴포넌트가 가로로 표시되도록 스타일 오버라이드
      :deep(.recommendations-container) {
        .recommendations-list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 1.5rem;
          
          @media (max-width: 1200px) {
            grid-template-columns: repeat(2, 1fr);
          }
          
          @media (max-width: 768px) {
            grid-template-columns: 1fr;
          }
        }
        
        .recommendation-item {
          margin-bottom: 0 !important;
          
          &:hover {
            transform: translateY(-2px) !important;
          }
        }
        
        .pagination {
          margin-top: 2rem;
          justify-content: center;
          
          .page-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
            
            &:hover:not(:disabled) {
              transform: translateY(-2px);
              box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }
            
            &:disabled {
              background: #f0f0f0;
              color: #aaa;
              transform: none;
              box-shadow: none;
            }
          }
          
          .page-info {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-weight: 600;
          }
        }
      }
    }
  }
}

// Sidebar Cards (현재 사용되지 않음)

.recommendations-header {
  margin-bottom: 2rem;
}

.recommendations-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  
  .recommendations-icon {
    font-size: 1.5rem;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  }
  
  h2 {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.recommendations-description {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 1rem;
  
  strong {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
  }
}

.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  color: #667eea;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.ai-icon {
  animation: pulse 2s infinite;
}

.recommendations-footer {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.accuracy-indicator {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.accuracy-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.accuracy-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.accuracy-progress {
  height: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.accuracy-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: #667eea;
  min-width: 40px;
}

.accuracy-tip {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
}

// Insights Card (삭제됨)

// Loading States
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 1rem;
  
  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(102, 126, 234, 0.1);
    border-left: 3px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  p {
    color: #667eea;
    font-weight: 600;
    font-size: 0.9rem;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// Empty States
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  text-align: center;
  
  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }
  
  h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: #666;
    font-size: 0.9rem;
  }
}



// Responsive Design
@media (max-width: 1024px) {
  .dashboard-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-stats {
    justify-content: center;
  }
  
  .floating-cards {
    display: none;
  }
}
</style>

