// 회원가입 페이지에서 회원가입 요청을 보내는 함수
import axios from 'axios';
import axiosInstance from "./axios";

const api = axios.create({
    baseURL: 'http://localhost:8000/accounts/',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export const authAPI = {
    // 로그인
    login: (credentials) => {
        return axiosInstance.post("/accounts/login/", {
            email: credentials.email,
            password: credentials.password
        });
    },

    // 회원가입
    register: (userData) => {
        return axiosInstance.post("/accounts/signup/", userData);
    },

    // 로그아웃
    logout: async () => {
        try {
            // 백엔드에 로그아웃 알림
            await axiosInstance.post("/accounts/logout/");
        } catch (error) {
            console.error("로그아웃 API 호출 실패:", error);
        } finally {
            // 클라이언트 측에서 토큰 및 사용자 정보 삭제
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            localStorage.removeItem("user");
        }
    },

    // 사용자 인증 상태 확인
    isAuthenticated: () => {
        return !!localStorage.getItem('access_token');
    },

    // 사용자 정보 가져오기
    getUserInfo: () => {
        return axiosInstance.get("/accounts/user/");
    },

    // JWT 토큰 갱신
    refreshToken: (refreshToken) => {
        return axiosInstance.post("/accounts/token/refresh/", { refresh: refreshToken });
    },

    // 사용자 활동 관련
    getUserActivity: (userId) => api.get(`${userId}/`),
    recordArticleView: (articleUrl) => api.post('article/view/', { url: articleUrl }),
    toggleArticleLike: (articleUrl) => api.post('article/like/', { url: articleUrl }),
    toggleArticleScrap: (articleUrl) => api.post('article/scrap/', { url: articleUrl }),
    checkArticleLike: (articleUrl) => api.get('article/check-like/', { params: { url: articleUrl } }),

    // 대시보드 관련
    getDashboardStats: () => api.get('dashboard/stats/'),
    getKeywordFrequency: () => api.get('dashboard/keywords/'),
    getWeeklyReads: () => api.get('dashboard/weekly-reads/'),
    getFavoriteArticles: () => api.get('dashboard/favorites/'),

    // 비밀번호 재설정 요청
    resetPassword: (email) => {
        return axiosInstance.post("/accounts/password/reset/", { email });
    },

    // 비밀번호 재설정 확인
    resetPasswordConfirm: (data) => {
        return axiosInstance.post("/accounts/password/reset/confirm/", data);
    },

    // 비밀번호 변경
    changePassword: (data) => {
        return axiosInstance.post("/accounts/password/change/", data);
    },

    // 사용자 정보 업데이트
    updateUserInfo: (data) => {
        return axiosInstance.patch("/accounts/user/", data);
    },

    // 이메일 인증 확인
    verifyEmail: (key) => {
        return axiosInstance.post("/accounts/registration/verify-email/", { key });
    },

    // 이메일 재전송
    resendEmail: (email) => {
        return axiosInstance.post("/accounts/registration/resend-email/", { email });
    },
};

export default api; 