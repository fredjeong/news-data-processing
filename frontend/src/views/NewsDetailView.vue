<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRoute } from "vue-router";
import axiosInstance from "@/utils/axios";
import ContentBox from "@/common/ContentBox.vue";
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import router from "@/router";
import ArticlePreview from "@/components/ArticlePreview.vue";
import { tabs } from "@/assets/data/tabs";
import ArticleRecommendations from "@/components/ArticleRecommendations.vue";

const route = useRoute();
const article = ref({});
const isLoading = ref(false);
const relatedNews = ref(null);
const { formatDate } = useDate();
const liked = ref(false);
const likeCount = ref(0);
const isAnimating = ref(false);
const isScrapped = ref(false);
const scrapCount = ref(0);

// 챗봇 관련 상태
const chatMessages = ref([]);
const userInput = ref("");
const isChatLoading = ref(false);
const isChatVisible = ref(false);

// 카테고리에 맞는 이모지 찾기
const categoryEmoji = computed(() => {
  const category = article.value.category;
  if (!category) return "";
  
  const tab = tabs.find(tab => tab.value === category);
  return tab ? tab.emoji : "🏷️"; // 매칭되는 카테고리가 없을 경우 기본 이모지 사용
});

const fetchArticle = async () => {
  try {
    isLoading.value = true;

    // 현재 기사 가져오기
    const response = await axiosInstance.get(`/articles/${route.params.id}/`);
    article.value = response.data;
    likeCount.value = article.value.like_count || 0;

    // 조회수 증가 - 로그인한 경우에만 기록
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        await axiosInstance.post(
          '/accounts/article/view/',
          { url: article.value.url }
        );
        console.log('조회 기록이 저장되었습니다.');
      } catch (viewError) {
        console.error('조회 기록 저장 중 오류:', viewError);
      }
    }

    // 좋아요 상태 확인
    await checkLikeStatus();
    // 스크랩 상태 확인
    await checkScrapStatus();

    // 전체 기사 목록 가져오기
    const allArticlesResponse = await axiosInstance.get(`/articles/`);
    const allArticles = allArticlesResponse.data;
    // 같은 카테고리의 다른 기사 필터링 (최대 3개)
    const filteredArticles = allArticles.filter(item =>
      item.id !== article.value.id &&
      item.category === article.value.category
    );
    relatedNews.value = filteredArticles
      .sort((a, b) => new Date(b.write_date) - new Date(a.write_date))
      .slice(0, 3);
  } catch (error) {
    console.error("Error fetching article:", error);
    alert('뉴스 기사를 불러오는데 실패했습니다.');
  } finally {
    isLoading.value = false;
  }
};

// 좋아요 상태 확인 함수
const checkLikeStatus = async () => {
  // 로그인 상태 확인
  const token = localStorage.getItem('access_token');
  if (!token) return;

  try {
    // 백엔드에서 좋아요 상태 확인
    const response = await axiosInstance.get('/accounts/article/check-like/', {
      params: { url: article.value.url }
    });
    
    // 좋아요 상태 업데이트
    liked.value = response.data.is_liked;
    console.log(`좋아요 상태: ${liked.value ? '좋아요 누름' : '좋아요 안누름'}`);
  } catch (error) {
    console.error('좋아요 상태 확인 중 오류:', error);
  }
};

// 스크랩 상태 확인 함수
const checkScrapStatus = async () => {
  // 로그인 상태 확인
  const token = localStorage.getItem('access_token');
  if (!token) return;

  try {
    const response = await axiosInstance.get('/accounts/article/check-scrap/', {
      params: { url: article.value.url }
    });
    
    // 스크랩 상태 업데이트 - 백엔드 응답의 키 이름 수정
    isScrapped.value = response.data.is_scraped;
    console.log(`스크랩 상태: ${isScrapped.value ? '스크랩됨' : '스크랩 안됨'}`);
  } catch (error) {
    console.error('스크랩 상태 확인 중 오류:', error);
  }
};

// 좋아요 토글 함수
const toggleLike = async () => {
  try {
    // 애니메이션 시작
    isAnimating.value = true;
    
    // 토큰 확인
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('로그인이 필요합니다.');
      return;
    }

    // 백엔드 API 호출
    const response = await axiosInstance.post(
      '/accounts/article/like/',
      { url: article.value.url }
    );

    // 백엔드 응답에 따라 좋아요 상태 및 카운트 업데이트
    if (response.status === 201) {  // 좋아요 등록됨
      liked.value = true;
      likeCount.value++;
      console.log('좋아요가 등록되었습니다.');
    } else if (response.status === 200) {  // 좋아요 취소됨
      liked.value = false;
      likeCount.value = Math.max(0, likeCount.value - 1);
      console.log('좋아요가 취소되었습니다.');
    }
  } catch (error) {
    console.error('좋아요 처리 중 오류 발생:', error);
    console.log(likeCount.value);
    alert('좋아요 처리 중 오류가 발생했습니다.');
  } finally {
    // 애니메이션 종료 (300ms 후)
    setTimeout(() => {
      isAnimating.value = false;
    }, 300);
  }
};

// 스크랩 토글 함수
const toggleScrap = async () => {
  try {
    // 애니메이션 시작
    isAnimating.value = true;
    
    // 토큰 확인
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('로그인이 필요합니다.');
      return;
    }

    // 백엔드 API 호출
    const response = await axiosInstance.post(
      '/accounts/article/scrap/',
      { url: article.value.url }
    );

    // 백엔드 응답에 따라 스크랩 상태 업데이트
    if (response.status === 201) {  // 스크랩 등록됨
      isScrapped.value = true;
      article.value.scrap_count = (article.value.scrap_count || 0) + 1;
      console.log('스크랩이 등록되었습니다.');
    } else if (response.status === 200) {  // 스크랩 취소됨
      isScrapped.value = false;
      article.value.scrap_count = Math.max(0, (article.value.scrap_count || 0) - 1);
      console.log('스크랩이 취소되었습니다.');
    }
  } catch (error) {
    console.error('스크랩 처리 중 오류 발생:', error);
    alert('스크랩 처리 중 오류가 발생했습니다.');
  } finally {
    // 애니메이션 종료 (300ms 후)
    setTimeout(() => {
      isAnimating.value = false;
    }, 300);
  }
};

// 챗봇 토글 함수
const toggleChat = () => {
  isChatVisible.value = !isChatVisible.value;
  
  // 챗봇이 처음 열릴 때 초기 메시지 추가
  if (isChatVisible.value && chatMessages.value.length === 0) {
    chatMessages.value.push({
      sender: 'bot',
      text: '안녕하세요! 이 기사에 대해 어떤 것이든 물어보세요.',
      timestamp: new Date()
    });
  }
};

// 챗봇 메시지 전송 함수
const sendMessage = async () => {
  if (!userInput.value.trim()) return;
  
  // 사용자 메시지 추가
  const userMessage = {
    sender: 'user',
    text: userInput.value,
    timestamp: new Date()
  };
  chatMessages.value.push(userMessage);
  
  // 입력 필드 초기화
  const message = userInput.value;
  userInput.value = "";
  
  // 로딩 상태 시작
  isChatLoading.value = true;
  
  try {
    // 백엔드 채팅 API 호출
    const response = await axiosInstance.post('/chatbot/chat/', {
      article_id: article.value.id,
      question: message
    });
    
    // 백엔드로부터 받은 응답을 채팅창에 추가
    chatMessages.value.push({
      sender: 'bot',
      text: response.data.bot_message.message,
      timestamp: new Date(response.data.bot_message.created_at)
    });
    
    isChatLoading.value = false;
  } catch (error) {
    console.error('챗봇 메시지 전송 중 오류:', error);
    chatMessages.value.push({
      sender: 'bot',
      text: '죄송합니다. 메시지 처리 중 오류가 발생했습니다.',
      timestamp: new Date()
    });
    isChatLoading.value = false;
  }
};

// route 파라미터 변경 감지
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    // 챗봇 상태 초기화
    isChatVisible.value = false;
    chatMessages.value = [];
    userInput.value = "";
    
    // 새 기사 로드
    fetchArticle();
  }
});

onMounted(() => {
  fetchArticle();
});
</script>

<template>
  <div class="news-detail-container">
    <!-- Hero Section -->
     <div v-if="!isLoading && article" class="article-hero">
      <div class="hero-background"></div>
      <div class="hero-content">
        <div class="article-meta">
          <div class="category-badge">
            <span class="category-emoji">{{ categoryEmoji }}</span>
            <span class="category-text">{{ article.category }}</span>
          </div>
          <div class="article-info">
            <span class="article-date">
              <span class="date-icon">📅</span>
              {{ formatDate(article.write_date) }}
            </span>
            <span class="article-author">
              <span class="author-icon">✍️</span>
              {{ article.writer }}
            </span>
          </div>
        </div>
 
        <h1 class="article-title">{{ article.title }}</h1>

        <div class="article-stats">
          <div class="stat-item">
            <span class="stat-icon">👀</span>
            <span class="stat-value">{{ article.article_interaction?.comments || article.view_count || 0 }}</span>
            <span class="stat-label">조회수</span>
          </div>
          <div class="stat-item">
            <span class="stat-icon">❤️</span>
            <span class="stat-value">{{ likeCount }}</span>
            <span class="stat-label">좋아요</span>
          </div>
          <div class="stat-item">
            <span class="stat-icon">📑</span>
            <span class="stat-value">{{ article.scrap_count || 0 }}</span>
            <span class="stat-label">스크랩</span>
          </div>
        </div>
      </div>
    </div>

    <div class="main-layout">
      <!-- 메인 콘텐츠 -->
      <div class="article-content">
        <!-- 기사 본문 -->
        <div v-if="!isLoading && article" class="content-card">
          <div class="content-header">
            <h2>📰 기사 본문</h2>
            <div class="reading-time">
              <span class="time-icon">⏱️</span>
              <span>약 {{ Math.ceil(article.content?.length / 500) || 3 }}분 읽기</span>
            </div>
          </div>
          
          <div class="article-body" v-html="article.content"></div>
          
          <div class="content-footer">
            <div class="engagement-actions">
              <button 
                @click="toggleLike" 
                class="action-button like-action"
                :class="{ 'liked': liked, 'animate': isAnimating }"
              >
                <span class="action-icon">❤️</span>
                <span class="action-text">{{ liked ? '좋아요 취소' : '좋아요' }}</span>
                <span class="action-count">{{ likeCount }}</span>
              </button>
              
              <a :href="article.url" target="_blank" class="action-button source-action">
                <span class="action-icon">🔗</span>
                <span class="action-text">원문 보기</span>
              </a>
              
              <button 
                @click="toggleScrap" 
                class="action-button scrap-action"
                :class="{ 'scrapped': isScrapped }"
              >
                <span class="action-icon">📑</span>
                <span class="action-text">{{ isScrapped ? '스크랩 취소' : '스크랩하기' }}</span>
              </button>
            </div>
          </div>
        </div>
      
        <!-- AI 챗봇 카드 -->
        <div v-if="!isLoading && article" class="chatbot-card">
          <div class="chatbot-header">
            <div class="chatbot-title">
              <span class="chatbot-icon">🤖</span>
              <h2>AI 기사 분석</h2>
            </div>
            <p class="chatbot-description">
              이 기사에 대해 궁금한 점을 AI에게 물어보세요
            </p>
            <button @click="toggleChat" class="chatbot-toggle">
              <span class="toggle-icon">{{ isChatVisible ? '📖' : '💬' }}</span>
              <span>{{ isChatVisible ? '챗봇 닫기' : '기사에 대해 물어보기' }}</span>
            </button>
          </div>
          
          <div v-if="isChatVisible" class="chatbot-interface">
            <div class="chat-messages">
              <div 
                v-for="(message, index) in chatMessages" 
                :key="index" 
                :class="['chat-message', message.sender === 'bot' ? 'bot-message' : 'user-message']"
              >
                <div class="message-avatar">
                  <span>{{ message.sender === 'bot' ? '🤖' : '👤' }}</span>
                </div>
                <div class="message-bubble">
                  <div class="message-text">{{ message.text }}</div>
                  <div class="message-time">
                    {{ new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                  </div>
                </div>
              </div>
              <div v-if="isChatLoading" class="typing-indicator">
                <div class="typing-avatar">
                  <span>🤖</span>
                </div>
                <div class="typing-bubble">
                  <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
            <div class="chat-input">
              <div class="input-wrapper">
                <input 
                  type="text" 
                  v-model="userInput" 
                  @keyup.enter="sendMessage"
                  placeholder="기사에 대해 질문해보세요..."
                  :disabled="isChatLoading"
                  class="message-input"
                />
                <button 
                  @click="sendMessage" 
                  :disabled="isChatLoading || !userInput.trim()" 
                  class="send-button"
                >
                  <span class="send-icon">🚀</span>
                </button>
              </div>
            </div>  
          </div>
        </div>
      </div>

      <!-- 사이드바 -->
      <div class="sidebar">
        <!-- 관련 기사 카드 -->
        <div v-if="relatedNews && relatedNews.length > 0" class="related-card">
          <div class="related-header">
            <h3>📰 같은 카테고리 기사</h3>
            <p>{{ article.category }} 분야의 다른 기사들</p>
          </div>
          <div class="related-list">
            <div v-for="news in relatedNews" :key="news.id" class="related-item">
              <ArticlePreview :to="`/news/${news.id}`" :news="news" />
            </div>
          </div>
        </div>
        
        <!-- AI 추천 기사 카드 -->
        <div class="recommendations-card">
          <div class="recommendations-header">
            <h3>🎯 AI 추천 기사</h3>
            <p>이 기사와 유사한 내용의 기사들</p>
          </div>
          <div class="recommendations-content">
            <ArticleRecommendations 
              v-if="!isLoading && article && article.id" 
              :articleId="article.id" 
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.news-detail-container {
  min-height: 100vh;
  padding-bottom: 4rem;
}

// Hero Section
.article-hero {
  position: relative;
  padding: 4rem 0;
  margin-bottom: 4rem;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: 
      radial-gradient(circle at 20% 80%, rgba(240, 147, 251, 0.2) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(102, 126, 234, 0.2) 0%, transparent 50%);
  }
}

.hero-content {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  animation: fadeInUp 0.8s ease-out;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 1rem;
  }
}

.category-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 1rem 2rem;
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  
  .category-emoji {
    font-size: 1.5rem;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  }
  
  .category-text {
    font-weight: 700;
    color: #667eea;
    font-size: 1.1rem;
  }
}

.article-info {
  display: flex;
  gap: 2rem;
  
  @media (max-width: 768px) {
    gap: 1rem;
  }
}

.article-date, .article-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-weight: 600;
  color: #555;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  
  .date-icon, .author-icon {
    font-size: 1.1rem;
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
  }
}

.article-title {
  font-size: 3rem;
  font-weight: 900;
  line-height: 1.2;
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  
  @media (max-width: 768px) {
    font-size: 2rem;
  }
}

.article-stats {
  display: flex;
  gap: 2rem;
  
  @media (max-width: 768px) {
    gap: 1rem;
    justify-content: center;
  }
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 1.5rem;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  min-width: 100px;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
  }
  
  .stat-icon {
    font-size: 1.5rem;
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

// Main Layout
.main-layout {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 3rem;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}

.article-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

// Content Card
.content-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 32px 64px rgba(0, 0, 0, 0.15);
  }
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  
  h2 {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

.reading-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 600;
  
  .time-icon {
    font-size: 1rem;
  }
}

.article-body {
  line-height: 1.8;
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 2rem;
  
  // 기사 본문 스타일링
  :deep(p) {
    margin-bottom: 1.5rem;
  }
  
  :deep(h1), :deep(h2), :deep(h3) {
    margin: 2rem 0 1rem;
    font-weight: 700;
    color: #1a1a1a;
  }
  
  :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 12px;
    margin: 2rem 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }
  
  :deep(blockquote) {
    border-left: 4px solid #667eea;
    padding-left: 1.5rem;
    margin: 2rem 0;
    font-style: italic;
    color: #555;
    background: rgba(102, 126, 234, 0.05);
    padding: 1rem 1.5rem;
    border-radius: 0 12px 12px 0;
  }
}

.content-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  padding-top: 2rem;
}

.engagement-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
}

.action-button {
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
  
  &:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: translateY(-2px);
  }
  
  &.liked {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
  }
  
  &.scrapped {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
  }
  
  .action-icon {
    font-size: 1.2rem;
  }
  
  .action-count {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.25rem 0.5rem;
    border-radius: 20px;
    font-size: 0.9rem;
  }
}

.source-action {
  background: rgba(79, 172, 254, 0.1);
  color: #4facfe;
  border-color: rgba(79, 172, 254, 0.2);
}

.chat-action {
  background: rgba(67, 233, 123, 0.1);
  color: #43e97b;
  border-color: rgba(67, 233, 123, 0.2);
}

@keyframes likeAnimation {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

// Chatbot Card
.chatbot-card {
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

.chatbot-header {
  text-align: center;
  margin-bottom: 2rem;
}

.chatbot-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
  
  .chatbot-icon {
    font-size: 2rem;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
    animation: pulse 2s infinite;
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

.chatbot-description {
  color: #666;
  font-size: 1rem;
  margin-bottom: 1.5rem;
}

.chatbot-toggle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 0 auto;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  .toggle-icon {
    font-size: 1.2rem;
  }
}

.chatbot-interface {
  margin-top: 2rem;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.chat-messages {
  height: 400px;
  overflow-y: auto;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-message {
  display: flex;
  gap: 1rem;
  max-width: 85%;
  
  &.bot-message {
    align-self: flex-start;
  }
  
  &.user-message {
    align-self: flex-end;
    flex-direction: row-reverse;
  }
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.message-bubble {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  
  .user-message & {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
  }
}

.message-text {
  line-height: 1.5;
  margin-bottom: 0.5rem;
  word-break: break-word;
}

.message-time {
  font-size: 0.8rem;
  opacity: 0.7;
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 1rem;
  align-self: flex-start;
  max-width: 85%;
}

.typing-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.typing-bubble {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.typing-dots {
  display: flex;
  gap: 0.5rem;
  
  span {
    width: 8px;
    height: 8px;
    background: #667eea;
    border-radius: 50%;
    animation: typingDots 1.4s infinite ease-in-out;
    
    &:nth-child(1) { animation-delay: 0s; }
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes typingDots {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.chat-input {
  background: white;
  padding: 1.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.input-wrapper {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: 2px solid rgba(102, 126, 234, 0.1);
  border-radius: 50px;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
  
  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #999;
  }
  
  &:disabled {
    background: #f5f5f5;
    cursor: not-allowed;
  }
}

.send-button {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover:not(:disabled) {
    transform: scale(1.1);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
  
  .send-icon {
    font-size: 1.2rem;
  }
}

// Sidebar
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  
  @media (max-width: 1024px) {
    order: -1;
  }
}

.related-card, .recommendations-card {
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

.related-card {
  top: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 1024px) {
    position: static;
  }
}

.recommendations-card {
  top: calc(2rem + 400px); // related-card의 높이를 고려한 위치
  
  @media (max-width: 1024px) {
    position: static;
  }
}

.related-header, .recommendations-header {
  margin-bottom: 1.5rem;
  
  h3 {
    font-size: 1.25rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: #666;
    font-size: 0.9rem;
  }
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.related-item {
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateX(4px);
  }
}

// Loading & Error States
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(102, 126, 234, 0.1);
  border-left: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-state p {
  color: #667eea;
  font-weight: 600;
  font-size: 1.1rem;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.error-state h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.5rem;
}

.error-state p {
  color: #666;
  font-size: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

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
@media (max-width: 768px) {
  .main-layout {
    padding: 0 1rem;
  }
  
  .content-card, .chatbot-card {
    padding: 2rem;
  }
  
  .article-hero {
    padding: 2rem 0;
  }
  
  .hero-content {
    padding: 0 1rem;
  }
  
  .engagement-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .chat-messages {
    height: 300px;
  }
}
</style>

