<script setup>
import { ref, onMounted, watch } from 'vue';
// useRouter는 더 이상 필요하지 않음 (RouterLink 사용)
import axiosInstance from '@/utils/axios';
import ArticlePreview from '@/components/ArticlePreview.vue';
import ContentBox from "@/common/ContentBox.vue";

const props = defineProps({
  articleId: {
    type: Number,
    required: true
  }
});

const recommendedArticles = ref([]);
const isLoading = ref(true);
const error = ref(null);
// router 변수 제거 (RouterLink 사용)

const fetchRecommendedArticles = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    
    const response = await axiosInstance.get(`/articles/${props.articleId}/related/`);
    recommendedArticles.value = response.data;
  } catch (err) {
    console.error('추천 기사를 가져오는 중 오류가 발생했습니다:', err);
    error.value = '추천 기사를 불러올 수 없습니다.';
  } finally {
    isLoading.value = false;
  }
};

// RouterLink를 통한 라우팅을 사용하므로 별도 핸들러 불필요

// articleId가 변경될 때마다 새로운 추천 기사 가져오기
watch(() => props.articleId, (newId) => {
  if (newId) {
    fetchRecommendedArticles();
  }
});

onMounted(() => {
  if (props.articleId) {
    fetchRecommendedArticles();
  }
});
</script>

<template>
  <div class="recommendations-container">
    <h3 class="recommendations-title">📋 관련 기사 추천</h3>
    <p class="recommendations-subtitle">읽고 있는 기사와 유사한 기사를 추천해드려요!</p>
    
    <div v-if="isLoading" class="loading">
      추천 기사를 불러오는 중...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="recommendedArticles.length === 0" class="empty">
      추천할 관련 기사가 없습니다.
    </div>
    
    <div v-else class="recommendations-list">
      <div 
        v-for="article in recommendedArticles" 
        :key="article.id" 
        class="recommendation-item"
      >
        <ArticlePreview 
          :news="article" 
          :to="`/news/${article.id}`"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.recommendations-container {
  margin-top: 30px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.recommendations-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}

.recommendations-subtitle {
  color: #666;
  margin-bottom: 15px;
  font-size: 14px;
}

.loading, .error, .empty {
  padding: 10px;
  text-align: center;
  color: #666;
  font-size: 14px;
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
  margin-bottom: 15px;
  cursor: pointer;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: translateX(5px);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
}
</style> 