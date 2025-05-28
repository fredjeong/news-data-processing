<script setup>
import { ref, onMounted, computed } from 'vue';
import axiosInstance from '@/utils/axios';
import ArticlePreview from '@/components/ArticlePreview.vue';
import { useRouter } from 'vue-router';

const recommendedArticles = ref([]);
const isLoading = ref(true);
const error = ref(null);
const currentPage = ref(1);
const itemsPerPage = 5;
const router = useRouter();

// 페이지별 아이템 계산
const paginatedArticles = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return recommendedArticles.value.slice(startIndex, endIndex);
});

// 총 페이지 수 계산
const totalPages = computed(() => {
  return Math.ceil(recommendedArticles.value.length / itemsPerPage);
});

// 페이지 변경 함수
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

const fetchRecommendedArticles = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    
    // 현재 로그인한 사용자 정보 가져오기
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = userData.id;
    
    if (!userId) {
      error.value = '사용자 정보를 찾을 수 없습니다.';
      return;
    }
    
    // 사용자 맞춤 추천 API 호출
    const response = await axiosInstance.get(`/accounts/${userId}/recommended/`);
    recommendedArticles.value = response.data;
    // 첫 페이지로 초기화
    currentPage.value = 1;
  } catch (err) {
    console.error('추천 기사를 가져오는 중 오류가 발생했습니다:', err);
    error.value = '추천 기사를 불러올 수 없습니다.';
  } finally {
    isLoading.value = false;
  }
};

const handleArticleClick = (articleId) => {
  router.push(`/news/${articleId}`);
};

onMounted(() => {
  fetchRecommendedArticles();
});
</script>

<template>
  <div class="recommendations-container">
    <div v-if="isLoading" class="loading">
      맞춤 추천 기사를 불러오는 중...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="recommendedArticles.length === 0" class="empty">
      추천할 맞춤 기사가 없습니다.<br>
      더 많은 기사를 읽고 좋아요를 누르면 더 정확한 추천을 받을 수 있어요!
    </div>
    
    <div v-else>
      <div class="recommendations-list">
        <div 
          v-for="article in paginatedArticles" 
          :key="article.id" 
          class="recommendation-item"
          @click="handleArticleClick(article.id)"
        >
          <ArticlePreview :news="article" />
        </div>
      </div>
      
      <!-- 페이지네이션 -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage === 1"
          class="page-btn"
        >
          &laquo; 이전
        </button>
        
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          다음 &raquo;
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.recommendations-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.loading, .error, .empty {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 200px;
  text-align: center;
  color: #666;
  font-style: italic;
  line-height: 1.5;
}

.error {
  color: #e74c3c;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recommendation-item {
  margin-bottom: 10px;
  cursor: pointer;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: translateX(5px);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
  
  .page-btn {
    padding: 5px 10px;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    
    &:hover:not(:disabled) {
      background-color: #e0e0e0;
    }
    
    &:disabled {
      color: #aaa;
      cursor: not-allowed;
    }
  }
  
  .page-info {
    font-size: 14px;
    color: #666;
  }
}
</style> 