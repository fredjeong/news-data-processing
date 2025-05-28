# 🤖 NEWRON Frontend

## 🎯 프로젝트 개요

사용자의 관심사와 읽기, 좋아요, 스크랩 등을 분석하여 개인화된 뉴스를 추천하는 AI 기반 뉴스 큐레이팅 서비스입니다. \
Vue.js 3를 기반으로 구축된  반응형 웹 애플리케이션입니다.


## 🛠 기술 스택

### Core Framework
- **Vue.js 3.5.12** - 프로그레시브 JavaScript 프레임워크
- **Vite 5.4.18** - 빠른 빌드 도구 및 개발 서버
- **Vue Router 4.4.5** - 공식 라우팅 라이브러리

### 상태 관리 & 데이터
- **Pinia 2.2.4** - Vue 3 공식 상태 관리 라이브러리
- **Pinia Plugin Persistedstate 4.1.2** - 상태 영속화
- **Axios 1.7.7** - HTTP 클라이언트

### UI & 시각화
- **Chart.js 4.4.5** - 데이터 시각화 라이브러리
- **Vue-ChartJS 5.3.1** - Vue용 Chart.js 래퍼
- **SCSS** - CSS 전처리기

### 개발 도구
- **Vite Plugin Vue DevTools** - Vue 개발자 도구
- **Sass Embedded** - SCSS 컴파일러
- **Unplugin Auto Import** - 자동 import 플러그인

## 📁 프로젝트 구조

```
src/
├── assets/                 
│   ├── data/               
│   │   └── tabs.js         # 카테고리 탭 데이터
│   ├── scss/               # 전역 스타일
│   ├── fonts.css           # 폰트 설정
│   └── logo.svg            # 로고 이미지
├── common/                 
│   ├── ContentBox.vue      # 컨텐츠 박스 래퍼
│   └── StateButton.vue     # 상태 버튼 컴포넌트
├── components/             
│   ├── TheHeader.vue       # 헤더 (네비게이션, 검색)
│   ├── TheFooter.vue       # 푸터
│   ├── NewsCard.vue        # 뉴스 카드
│   ├── ArticlePreview.vue  # 기사 미리보기
│   ├── UserRecommendations.vue # 사용자 맞춤 추천
│   ├── ArticleRecommendations.vue # 관련 기사 추천
│   ├── BoardCard.vue       # 게시판 카드
│   └── CommentBox.vue      # 댓글 박스
├── composables/            
│   ├── useDate.js          # 날짜 포맷팅
│   └── useValidation.js    # 폼 검증
├── router/                 # 라우팅 설정
│   └── index.js            # 라우터 구성
├── utils/                  # 유틸리티 함수
│   ├── axios.js            # Axios 인스턴스 설정
│   └── api.js              # 인증 관련 API 호출 함수
├── views/                  
│   ├── NewsView.vue        # 뉴스 목록 페이지
│   ├── NewsDetailView.vue  # 뉴스 상세 페이지
│   ├── DashBoardView.vue   # 대시보드 페이지
│   ├── LoginView.vue       # 로그인 페이지
│   ├── RegisterView.vue    # 회원가입 페이지
│   ├── SearchResultView.vue # 검색 결과 페이지
│   └── NotFoundView.vue    # 404 페이지
├── App.vue                 # 루트 컴포넌트
└── main.js                 # 애플리케이션 진입점
```

## 🚀 주요 기능

### 1. 사용자 인증 시스템
**구현 위치**: `LoginView.vue`, `RegisterView.vue`
**기술 스택**: JWT 토큰, Axios 인터셉터

```javascript
// JWT 토큰 자동 갱신 (utils/axios.js)
instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !originalRequest._retry) {
      // 토큰 갱신 로직
      const refreshToken = localStorage.getItem("refresh_token");
      const response = await axios.post("/accounts/token/refresh/", {
        refresh: refreshToken,
      });
      localStorage.setItem("access_token", response.data.access);
      return instance(originalRequest);
    }
  }
);
```
**Logic**:
- 백엔드에서 Token 발급
    ```json
    {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
- localStorage에 저장
    ```js
    localStorage.setItem('accessToken', accessToken);
    ```
- API 호출 시 Authorization 헤더에 토큰 넣기
    ```js
    const token = localStorage.getItem('accessToken');
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    ```

**주요 특징**:
- 자동 토큰 갱신으로 끊김 없는 사용자 경험
- 라우터 가드를 통한 인증 상태 관리
- 로그인 후 이전 페이지로 자동 리다이렉트

### 2. 카테고리 탭
**구현 위치**: `NewsView.vue`
**기술 스택**: Vue 3 Composition API, SCSS

```javascript
<div class="news__tabs-container">
  <div class="news__tabs">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      class="tab-item"
      :class="{ 'tab-item--active': activeTab === tab.id }"
      @click="activeTab = tab.id"
    >
      <span class="tab-emoji">{{ tab.emoji }}</span>
      <span class="tab-label">{{ tab.label }}</span>
    </button>
  </div>
</div>
```

**주요 특징**:
- 18개 뉴스 카테고리 (정치, 경제, 문화, IT/과학 등)
- 이모지와 텍스트가 결합된 직관적 디자인
- 호버 효과와 선택 상태 시각화

### 3. 실시간 뉴스 검색
**구현 위치**: `TheHeader.vue`, `SearchResultView.vue`
**기술 스택**: Vue Router, Axios

```javascript
<!-- 검색 폼 (TheHeader.vue) -->
<form class="form" @submit="handleSearch">
  <button type="submit">
    <svg><!-- 검색 아이콘 --></svg>
  </button>
  <input v-model="searchQuery" placeholder="뉴스 키워드 검색" type="text">
  <button class="reset" type="reset" @click="searchQuery = ''">
    <svg><!-- 리셋 아이콘 --></svg>
  </button>
</form>
```

**주요 특징**:
- 실시간 키워드 검색
- 검색 결과 하이라이팅
- 검색 히스토리 관리
- 애니메이션 효과가 적용된 검색 바

### 4. 개인화 대시보드
**구현 위치**: `DashBoardView.vue`
**기술 스택**: Chart.js, Vue-ChartJS

```javascript
<!-- 차트 컴포넌트 -->
<template>
  <Bar :data="keywordData" :options="barOptions" />
  <Doughnut :data="categoryData" :options="options" />
</template>

<script setup>
import { Bar, Doughnut } from "vue-chartjs";
import { Chart as ChartJS, ArcElement, BarElement } from "chart.js";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale);
</script>
```

**주요 특징**:
- **통계 카드**: 총 읽은 기사 수, 좋아요 수
- **관심 카테고리 차트**: 도넛 차트로 카테고리별 선호도 시각화
- **키워드 분석**: 가로 막대 차트로 주요 키워드 빈도 표시
- **주간 읽기 패턴**: 최근 7일간 읽은 기사 수 추이
- **좋아요한 기사 목록**: 스크롤 가능한 기사 리스트

### 5. AI 맞춤 추천 시스템
**구현 위치**: `UserRecommendations.vue`
**기술 스택**: Vue 3 Composition API, Pagination

```javascript
// 맞춤 추천 API 호출
const fetchRecommendedArticles = async () => {
  const userData = JSON.parse(localStorage.getItem('user') || '{}');
  const userId = userData.id;
  
  const response = await axiosInstance.get(`/accounts/${userId}/recommended/`);
  recommendedArticles.value = response.data;
};

// 페이지네이션 처리
const paginatedArticles = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return recommendedArticles.value.slice(startIndex, endIndex);
});
```

**주요 특징**:
- 사용자 읽기 패턴 기반 개인화 추천
- 페이지네이션으로 성능 최적화
- 추천 이유 표시 (관심 카테고리, 키워드 매칭)

### 6. 뉴스 상세 페이지
**구현 위치**: `NewsDetailView.vue`
**기술 스택**: Vue Router, Dynamic Routing

```javascript
// 동적 라우팅으로 기사 ID 전달
{
  path: "/news/:id",
  name: "newsDetail",
  component: NewsDetailView,
  props: true,
  meta: { requiresAuth: true },
}

// 관련 기사 추천
const fetchRelatedArticles = async () => {
  const response = await axiosInstance.get(`/articles/${articleId}/related/`);
  relatedArticles.value = response.data;
};
```

**주요 특징**:
- 기사 전문 표시 및 원문 링크
- 좋아요 기능
- 관련 기사 및 같은 카테고리 기사 추천
- Chatbot UI

## 🧩 컴포넌트 구조

### Common Components (공통 컴포넌트)

#### ContentBox.vue
```js
<!-- 재사용 가능한 컨텐츠 박스 -->
<template>
  <div class="box">
    <slot />
  </div>
</template>

<style>
.box {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
```

#### StateButton.vue
```js
<!-- 다양한 상태를 표현하는 버튼 -->
<template>
  <button 
    :class="[
      'state-button',
      `state-button--${type}`,
      `state-button--${size}`,
      { 'state-button--active': isActive }
    ]"
  >
    <span v-if="showEmoji">{{ getEmoji(category) }}</span>
    <slot />
  </button>
</template>
```

**사용 예시**:
- 카테고리 태그: `type="state"`, `category="정치"`
- 키워드 태그: `type="tag"`, `size="sm"`
- 활성 상태: `isActive="true"`

### Feature Components (기능 컴포넌트)

#### NewsCard.vue
```js
<!-- 뉴스 카드 컴포넌트 -->
<template>
  <div class="card">
    <div class="card__header">
      <StateButton :category="article.category">
        {{ article.category }}
      </StateButton>
      <span>{{ article.writer }} · {{ formatDate(article.write_date) }}</span>
    </div>
    
    <RouterLink :to="{ name: 'newsDetail', params: { id: article.id } }">
      <h2>{{ article.title }}</h2>
      <p>{{ article.summary }}</p>
    </RouterLink>
    
    <div class="stats">
      <span>❤️ {{ article.like_count }}</span>
      <span>👀 {{ article.view_count }}</span>
    </div>
    
    <div class="tags">
      <StateButton v-for="tag in processedKeywords" type="tag">
        #{{ tag }}
      </StateButton>
    </div>
  </div>
</template>
```

**주요 기능**:
- 기사 메타데이터 표시 (카테고리, 작성자, 날짜)
- 제목과 요약 표시
- 통계 정보 (좋아요, 조회수)
- 키워드 태그 표시
- 상세 페이지로 라우팅

## 🛣 라우팅 시스템

### 라우트 구성
```js
const router = createRouter({
  history: createWebHistory("/"),
  routes: [
    {
      path: "/",
      redirect: "/news",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { requiresAuth: false },
    },
    {
      path: "/register",
      name: "register",
      component: RegisterView,
      meta: { requiresAuth: false },
    },
    {
      path: "/news",
      name: "News",
      component: NewsView,
      meta: { requiresAuth: false },
    },
    {
      path: "/news/:id",
      name: "newsDetail",
      component: NewsDetailView,
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashBoardView,
      meta: { requiresAuth: true },
    },
    {
      path: "/mypage",
      name: "mypage",
      component: MyPageView,
      meta: { requiresAuth: true },
    },
    {
      path: "/search",
      name: "search",
      component: SearchResultView,
      meta: { requiresAuth: false },
    },
    {
      path: "/:pathMatch(.*)*",
      component: NotFoundView,
    },
  ],
});
```

### 네비게이션 가드
- 로그인 여부에 따른 라우팅 구현
```javascript
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('access_token');
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login'); // 인증 필요 시 로그인 페이지로
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    next('/'); // 이미 로그인된 사용자는 메인으로
  } else {
    next();
  }
});
```

## 🗄 상태 관리

### Pinia Store 구조
```javascript
// stores/auth.js (예시)
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    isAuthenticated: false
  }),
  
  actions: {
    async login(credentials) {
      const response = await api.login(credentials);
      this.setAuth(response.data);
    },
    
    setAuth(authData) {
      this.user = authData.user;
      this.token = authData.access_token;
      this.isAuthenticated = true;
      localStorage.setItem('access_token', authData.access_token);
    }
  },
  
  persist: true // 상태 영속화
});
```

## 🌐 API 통신

### Axios 인스턴스 설정
```javascript
// utils/axios.js
const instance = axios.create({
  baseURL: "http://localhost:8000",
  headers: { 'Content-Type': 'application/json' }
});

// 요청 인터셉터 - JWT 토큰 자동 추가
instance.interceptors.request.use(config => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터 - 토큰 갱신 처리
instance.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // 토큰 갱신 로직
      await refreshToken();
      return instance(error.config);
    }
    return Promise.reject(error);
  }
);
```

### API 엔드포인트
```javascript
// utils/api.js
export const newsAPI = {
  // 뉴스 목록 조회
  getNews: () => instance.get('/articles/'),
  
  // 뉴스 상세 조회
  getNewsDetail: (id) => instance.get(`/articles/${id}/`),
  
  // 사용자 맞춤 추천
  getRecommendations: (userId) => instance.get(`/accounts/${userId}/recommended/`),
  
  // 대시보드 데이터
  getDashboardStats: () => instance.get('/accounts/dashboard/stats/'),
  
  // 검색
  searchNews: (query) => instance.get(`/articles/search/?q=${query}`)
};
```

## 🎨 스타일링 시스템

### SCSS 구조
```scss
// assets/scss/main.scss
@import 'variables';
@import 'mixins';
@import 'base';
@import 'components';

// CSS 변수 활용
:root {
  --primary-color: #4a90e2;
  --secondary-color: #f5f5f5;
  --text-color: #333;
  --border-color: #e5e7eb;
  --shadow: 0px 1px 3px rgba(0, 0, 0, 0.1);
}
```

### 반응형 디자인
```scss
// 모바일 우선 접근법
.component {
  // 모바일 스타일 (기본)
  padding: 10px;
  
  // 태블릿
  @media (min-width: 768px) {
    padding: 20px;
  }
  
  // 데스크톱
  @media (min-width: 1024px) {
    padding: 30px;
  }
}
```

## 📦 설치 및 실행

### 요구사항
- Node.js 16.0.0 이상
- npm 7.0.0 이상

### 설치
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build

# 프리뷰 (빌드 결과 확인)
npm run serve
```

## 🚀 빌드 및 배포

### 프로덕션 빌드
```bash
npm run build
```

## 🔧 개발 가이드

### 컴포넌트 개발 규칙
1. **Single File Component** 구조 사용
2. **Composition API** 우선 사용
3. **Props 타입 정의** 필수
4. **Emit 이벤트 명시적 정의**

```js
<script setup>
// Props 정의
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  items: {
    type: Array,
    default: () => []
  }
});

// Emits 정의
const emit = defineEmits(['update', 'delete']);

// 반응형 데이터
const isLoading = ref(false);
const selectedItem = ref(null);

// 계산된 속성
const filteredItems = computed(() => {
  return props.items.filter(item => item.active);
});

// 메서드
const handleUpdate = (item) => {
  emit('update', item);
};
</script>
```

## 🐛 트러블슈팅

### 자주 발생하는 문제들

#### 1. CORS 에러
```javascript
// vite.config.js에서 프록시 설정
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});
```

## 📈 향후 개선사항

- [ ] 다크 모드 구현
- [ ] 오프라인 읽기 기능
- [ ] 서버사이드 렌더링 (Nuxt.js)
- [ ] 성능 모니터링 시스템
- [ ] 모바일 앱 개발 (React Native/Flutter)
- [ ] AI 챗봇 고도화
- [ ] 다국어 지원

### 코딩 컨벤션
- **변수명**: camelCase
- **컴포넌트명**: PascalCase
- **파일명**: kebab-case
- **상수**: UPPER_SNAKE_CASE

---

**NEWRON Frontend** - AI가 만드는 나만의 뉴스 경험 🚀