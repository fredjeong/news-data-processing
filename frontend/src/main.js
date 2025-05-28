import "@/assets/scss/main.scss";
import { createApp } from "vue";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import App from "@/App.vue";
import router from "@/router";
import { createPinia } from "pinia";
import axios from 'axios';

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

// Axios 기본 설정
axios.defaults.baseURL = 'http://localhost:8000';  // 백엔드 서버 주소
axios.defaults.headers.common['Content-Type'] = 'application/json';

// JWT 토큰이 있으면 모든 요청에 포함
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

app.use(pinia);
app.use(router);

app.mount("#app");
