<script setup>
import { ref, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { computed } from "vue";
import axiosInstance from "@/utils/axios";

const router = useRouter();
const searchQuery = ref("");
const suggestions = ref([]);
const showSuggestions = ref(false);
const selectedSuggestionIndex = ref(-1);
const searchInputRef = ref(null);

const isLoggedIn = computed(() => {
  return !!localStorage.getItem("access_token");
});

const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  router.push("/login");
};

const refreshPage = (event) => {
  event.preventDefault();
  router.push("/").then(() => {
    window.location.reload();
  });
};

// 자동완성 관련 함수들
const fetchSuggestions = async (query) => {
  if (!query || query.length < 2) {
    suggestions.value = [];
    showSuggestions.value = false;
    return;
  }

  try {
    const response = await axiosInstance.get(`/articles/api/suggest/?q=${encodeURIComponent(query)}`);
    suggestions.value = response.data.suggestions || [];
    showSuggestions.value = suggestions.value.length > 0;
    selectedSuggestionIndex.value = -1;
  } catch (error) {
    console.error('자동완성 데이터를 가져오는 중 오류가 발생했습니다:', error);
    suggestions.value = [];
    showSuggestions.value = false;
  }
};

// 검색어 변경 시 자동완성 실행 (디바운싱)
let debounceTimer = null;
watch(searchQuery, (newQuery) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchSuggestions(newQuery);
  }, 300);
});

const handleSearch = (event) => {
  event.preventDefault();
  const query = searchQuery.value.trim();
  if (query) {
    hideSuggestions();
    router.push({
      path: '/search',
      query: { q: query }
    });
  }
};

const selectSuggestion = (suggestion) => {
  searchQuery.value = suggestion.text;
  hideSuggestions();
  router.push({
    path: '/search',
    query: { q: suggestion.text }
  });
};

const hideSuggestions = () => {
  showSuggestions.value = false;
  selectedSuggestionIndex.value = -1;
};

const handleKeydown = (event) => {
  if (!showSuggestions.value || suggestions.value.length === 0) return;

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      selectedSuggestionIndex.value = Math.min(
        selectedSuggestionIndex.value + 1,
        suggestions.value.length - 1
      );
      break;
    case 'ArrowUp':
      event.preventDefault();
      selectedSuggestionIndex.value = Math.max(selectedSuggestionIndex.value - 1, -1);
      break;
    case 'Enter':
      event.preventDefault();
      if (selectedSuggestionIndex.value >= 0) {
        selectSuggestion(suggestions.value[selectedSuggestionIndex.value]);
      } else {
        handleSearch(event);
      }
      break;
    case 'Escape':
      hideSuggestions();
      break;
  }
};

const handleInputFocus = () => {
  if (searchQuery.value.length >= 2 && suggestions.value.length > 0) {
    showSuggestions.value = true;
  }
};

const handleInputBlur = () => {
  // 약간의 지연을 두어 클릭 이벤트가 처리될 수 있도록 함
  setTimeout(() => {
    hideSuggestions();
  }, 200);
};

</script>

<template>
  <div class="header__container">
    <header class="header">
      <router-link to="/" @click="refreshPage" class="logo-container">
        <div class="logo">
          <span class="logo-icon">🚀</span>
          <span class="logo-text">NEWRON</span>
          <div class="logo-glow"></div>
        </div>
      </router-link>

      <nav class="navigation">
        <form class="search-form" @submit="handleSearch">
          <div class="search-container">
            <button type="submit" class="search-button">
              <svg width="20" height="20" fill="none" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <input 
              ref="searchInputRef"
              v-model="searchQuery" 
              class="search-input" 
              placeholder="AI가 뉴스를 찾아드려요..." 
              type="text"
              @keydown="handleKeydown"
              @focus="handleInputFocus"
              @blur="handleInputBlur"
              autocomplete="off"
            >
            <button 
              v-if="searchQuery" 
              class="clear-button" 
              type="button" 
              @click="searchQuery = ''; hideSuggestions();"
            >
              <svg width="16" height="16" fill="none" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            
            <!-- 자동완성 드롭다운 -->
            <div 
              v-if="showSuggestions && suggestions.length > 0" 
              class="suggestions-dropdown"
            >
              <div 
                v-for="(suggestion, index) in suggestions" 
                :key="index"
                class="suggestion-item"
                :class="{ 'selected': index === selectedSuggestionIndex }"
                @click="selectSuggestion(suggestion)"
                @mouseenter="selectedSuggestionIndex = index"
              >
                <div class="suggestion-text">{{ suggestion.text }}</div>  
              </div>
            </div>
          </div>
        </form>

        <div class="nav-links">
          <router-link to="/news" class="nav-link">
            <span class="nav-icon">🎯</span>
            <span>맞춤 뉴스</span>
          </router-link>
          <router-link to="/dashboard" class="nav-link">
            <span class="nav-icon">📊</span>
            <span>대시보드</span>
          </router-link>
          <router-link v-if="isLoggedIn" to="/mypage" class="nav-link">
            <span class="nav-icon">👤</span>
            <span>마이페이지</span>
          </router-link>
          <button v-if="isLoggedIn" @click="logout" class="auth-button logout">
            <span class="nav-icon">👋</span>
            <span>로그아웃</span>
          </button>
          <router-link v-else to="/login" class="auth-button login">
            <span class="nav-icon">✨</span>
            <span>로그인</span>
          </router-link>
        </div>
      </nav>
    </header>
  </div>
</template>

<style scoped lang="scss">
.header__container {
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header {
  max-width: 1400px;
  margin: 0 auto;
  height: 80px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  
  @media (max-width: 768px) {
    padding: 0 1rem;
    height: 70px;
  }
}

.logo-container {
  text-decoration: none;
  position: relative;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
  padding: 0.5rem 1rem;
  border-radius: 16px;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    
    .logo-glow {
      opacity: 1;
      transform: scale(1.1);
    }
    
    .logo-icon {
      animation: pulse 1s infinite;
    }
  }
}

.logo-glow {
  position: absolute;
  inset: -4px;
  background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
  border-radius: 20px;
  opacity: 0;
  z-index: -1;
  filter: blur(8px);
  transition: all 0.3s ease;
}

.logo-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.5));
}

.logo-text {
  font-size: 1.75rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

.navigation {
  display: flex;
  align-items: center;
  gap: 2rem;
  
  @media (max-width: 768px) {
    gap: 1rem;
  }
}

.search-form {
  position: relative;
}

.search-container {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid transparent;
  border-radius: 50px;
  padding: 0.75rem 1.25rem;
  min-width: 320px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), 0 8px 32px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
  
  @media (max-width: 768px) {
    min-width: 200px;
  }
}

.search-button {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
    transform: scale(1.1);
  }
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  color: #333;
  
  &::placeholder {
    color: #999;
    font-weight: 400;
  }
  
  &:focus {
    outline: none;
  }
}

.clear-button {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 0, 0, 0.1);
    color: #ff4757;
    transform: scale(1.1);
  }
}

// 자동완성 드롭다운 스타일
.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 16px;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), 0 20px 40px rgba(0, 0, 0, 0.15);
  border: 2px solid #667eea;
  backdrop-filter: blur(20px);
  z-index: 1000;
  max-height: 300px;
  margin-top: 8px;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover,
  &.selected {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    transform: translateX(4px);
  }
  
  &:first-child {
    border-radius: 16px 16px 0 0;
  }
  
  &:last-child {
    border-radius: 0 0 16px 16px;
  }
  
  &:only-child {
    border-radius: 16px;
  }
}

.suggestion-text {
  flex: 1;
  font-size: 14px;
  color: #333;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 12px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link, .auth-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #667eea, #764ba2);
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: -1;
  }
  
  &:hover {
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    
    &::before {
      opacity: 1;
    }
    
    .nav-icon {
      animation: pulse 0.6s ease;
    }
  }
  
  &.router-link-active {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }
}

.auth-button {
  border: none;
  background: transparent;
  cursor: pointer;
  color: #333;
  
  &.login {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    
    &:hover {
      transform: translateY(-2px) scale(1.05);
      box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
  }
  
  &.logout {
    &:hover {
      background: linear-gradient(135deg, #ff6b6b, #ee5a52);
      
      &::before {
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
      }
    }
  }
}

.nav-icon {
  font-size: 1.1rem;
  filter: drop-shadow(0 0 4px rgba(0, 0, 0, 0.1));
}

@media (max-width: 768px) {
  .nav-link span:not(.nav-icon),
  .auth-button span:not(.nav-icon) {
    display: none;
  }
  
  .search-container {
    min-width: 150px;
  }
}
</style>
