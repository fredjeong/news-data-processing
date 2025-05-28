<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import axiosInstance from '@/utils/axios';
import NewsCard from '@/components/NewsCard.vue';

const route = useRoute();
const searchResults = ref([]);
const isLoading = ref(false);
const error = ref(null);
const searchQuery = ref('');
const totalResults = ref(0);

onMounted(() => {
  searchQuery.value = route.query.q || '';
  if (searchQuery.value) {
    fetchSearchResults();
  }
});

// 라우트 쿼리 파라미터가 변경될 때마다 검색 실행
watch(() => route.query.q, (newQuery) => {
  searchQuery.value = newQuery || '';
  if (searchQuery.value) {
    fetchSearchResults();
  }
});

const fetchSearchResults = async () => {
  if (!searchQuery.value) return;
  
  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await axiosInstance.get(`/articles/api/search/?q=${encodeURIComponent(searchQuery.value)}`);
    searchResults.value = (response.data.results || []).slice(0, 5);
    totalResults.value = response.data.results?.length || 0;
  } catch (err) {
    console.error('검색 결과를 가져오는 중 오류가 발생했습니다:', err);
    error.value = '검색 결과를 가져오는 데 실패했습니다. 나중에 다시 시도해주세요.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="search-results-container">
    <div class="search-header">
      <h1>"{{ searchQuery }}" 검색 결과</h1>
      <p v-if="searchResults.length > 0">{{ totalResults }}개의 기사를 찾았습니다.</p>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>검색 중...</p>
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else-if="searchResults.length === 0 && searchQuery" class="no-results">
      <p>검색 결과가 없습니다. 다른 검색어를 시도해보세요.</p>
    </div>

    <div v-else class="search-results">
      <div v-for="article in searchResults" :key="article.id" class="search-result-item">
        <NewsCard :article="article" :searchQuery="searchQuery" />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.search-results-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 20px 15px;
}

.search-header {
  margin-bottom: 30px;
  
  h1 {
    font-size: 28px;
    margin-bottom: 10px;
  }
  
  p {
    color: #666;
    margin-bottom: 20px;
  }
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.search-result-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  background-color: white;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-left-color: #2f2ee9;
    animation: spin 1s linear infinite;
    margin-bottom: 15px;
  }
}

.error-message, .no-results {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 