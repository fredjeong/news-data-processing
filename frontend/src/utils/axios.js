import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    'Content-Type': 'application/json',
  }
});

// 요청 인터셉터
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
instance.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // 토큰 만료 에러 처리 (401)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // JWT 토큰 갱신
        const refreshToken = localStorage.getItem("refresh_token");
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }
        
        const response = await axios.post("http://localhost:8000/accounts/token/refresh/", {
          refresh: refreshToken,
        });

        if (response.data.access) {
          localStorage.setItem("access_token", response.data.access);
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          return instance(originalRequest);
        } else {
          throw new Error('Failed to get new access token');
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        
        // 리프레시 토큰도 만료된 경우 로그아웃 처리
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
        
        // 로그인 페이지로 이동하기 전 현재 URL 저장 (리다이렉트용)
        if (window.location.pathname !== '/login') {
          sessionStorage.setItem('redirect_after_login', window.location.pathname);
        }
        
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default instance; 