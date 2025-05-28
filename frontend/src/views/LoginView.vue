<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import StateButton from "@/common/StateButton.vue";
import { authAPI } from "@/utils/api";

const router = useRouter();
const email = ref("");
const password = ref("");
const error = ref("");
const isLoading = ref(false);

const login = async () => {
  isLoading.value = true;
  error.value = "";
  
  try {
    // 이메일 및 비밀번호 입력 확인
    if (!email.value || !password.value) {
      error.value = "이메일과 비밀번호를 모두 입력해주세요.";
      isLoading.value = false;
      return;
    }

    // authAPI를 사용하여 로그인 요청
    const response = await authAPI.login({
      email: email.value,
      password: password.value,
    });

    // JWT 토큰 저장
    if (response.data.access) {
      localStorage.setItem("access_token", response.data.access);
      localStorage.setItem("refresh_token", response.data.refresh);
      
      // 사용자 정보 저장
      if (response.data.user) {
        localStorage.setItem("user", JSON.stringify(response.data.user));
      }
      
      // 로그인 성공 메시지 처리
      console.log(response.data.message || "로그인이 성공적으로 완료되었습니다.");
      
      // 로그인 성공 후 메인 페이지로 이동
      router.push("/");
    } else {
      throw new Error("인증 토큰을 받지 못했습니다.");
    }
  } catch (err) {
    console.error("Login error:", err);
    
    if (err.response && err.response.data) {
      // 백엔드의 에러 메시지 형식에 맞게 처리
      if (typeof err.response.data === 'object') {
        if (err.response.data.non_field_errors) {
          error.value = err.response.data.non_field_errors[0];
        } else if (err.response.data.detail) {
          error.value = err.response.data.detail;
        } else if (err.response.data.message) {
          error.value = err.response.data.message;
        } else if (err.response.data.status === 401) {
          error.value = "이메일 또는 비밀번호가 올바르지 않습니다.";
        } else {
          error.value = "이메일 또는 비밀번호가 올바르지 않습니다.";
        }
      } else {
        error.value = "이메일 또는 비밀번호가 올바르지 않습니다.";
      }
    } else {
      error.value = "로그인에 실패했습니다. 잠시 후 다시 시도해주세요.";
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="login-page">
    <!-- Hero Background -->
    <div class="hero-background">
      <div class="floating-elements">
        <div class="floating-element element-1">🔐</div>
        <div class="floating-element element-2">✨</div>
        <div class="floating-element element-3">🚀</div>
        <div class="floating-element element-4">💎</div>
        <div class="floating-element element-5">🌟</div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="login-container">
      <!-- Left Side - Hero Content -->
      <div class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">
            <span class="title-gradient">NEWRON</span>

          </h1>
          <p class="hero-description">
            개인화된 뉴스 경험을 위해<br>
            <strong>안전하게 로그인</strong>하세요
          </p>
          <div class="hero-features">
            <div class="feature-item">
              <span class="feature-icon">🤖</span>
              <span>AI 맞춤 추천</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">📊</span>
              <span>개인 대시보드</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">❤️</span>
              <span>즐겨찾기 관리</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Login Form -->
      <div class="form-section">
        <div class="login-card">
          <div class="card-header">
            <h2 class="card-title">NEWRON 로그인</h2>
            <p class="card-subtitle">계정에 로그인하여 개인화된 뉴스를 만나보세요</p>
          </div>

          <form @submit.prevent="login" class="login-form">
            <div class="input-group">
              <label for="email" class="input-label">
                <span class="label-icon">📧</span>
                이메일
              </label>
              <div class="input-wrapper">
                <input
                  type="email"
                  id="email"
                  v-model="email"
                  placeholder="이메일을 입력하세요"
                  class="form-input"
                  required
                />
                <div class="input-border"></div>
              </div>
            </div>

            <div class="input-group">
              <label for="password" class="input-label">
                <span class="label-icon">🔒</span>
                비밀번호
              </label>
              <div class="input-wrapper">
                <input
                  type="password"
                  id="password"
                  v-model="password"
                  placeholder="비밀번호를 입력하세요"
                  class="form-input"
                  required
                />
                <div class="input-border"></div>
              </div>
            </div>

            <div v-if="error" class="error-message">
              <span class="error-icon">⚠️</span>
              {{ error }}
            </div>

            <StateButton 
              type="submit" 
              class="login-button"
              :loading="isLoading"
            >
              <span v-if="!isLoading" class="button-content">
                <span class="button-icon">🚀</span>
                로그인
              </span>
              <span v-else class="button-content">
                <span class="loading-spinner"></span>
                로그인 중...
              </span>
            </StateButton>
          </form>

          <div class="form-footer">
            <div class="divider">
              <span class="divider-text">OR</span>
            </div>
            <div class="auth-links">
              <router-link to="/register" class="auth-link primary">
                <span class="link-icon">✨</span>
                회원가입
              </router-link>
              <router-link to="/find-password" class="auth-link secondary">
                <span class="link-icon">🔍</span>
                비밀번호 찾기
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

// Hero Background
.hero-background {
  position: fixed;
  inset: 0;
  background: linear-gradient(
    135deg,
    #667eea 0%,
    #764ba2 25%,
    #f093fb 50%,
    #f5576c 75%,
    #4facfe 100%
  );
  z-index: -1;
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(
      circle at 20% 80%,
      rgba(120, 119, 198, 0.3),
      transparent 50%
    ),
    radial-gradient(
      circle at 80% 20%,
      rgba(255, 119, 198, 0.3),
      transparent 50%
    );
  }
}

.floating-elements {
  position: absolute;
  inset: 0;
}

.floating-element {
  position: absolute;
  font-size: 2rem;
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;
  
  &.element-1 {
    top: 10%;
    left: 10%;
    animation-delay: 0s;
  }
  
  &.element-2 {
    top: 20%;
    right: 20%;
    animation-delay: 1s;
  }
  
  &.element-3 {
    bottom: 30%;
    left: 15%;
    animation-delay: 2s;
  }
  
  &.element-4 {
    bottom: 20%;
    right: 10%;
    animation-delay: 3s;
  }
  
  &.element-5 {
    top: 50%;
    left: 50%;
    animation-delay: 4s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

// Main Container
.login-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

// Hero Section
.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  
  @media (max-width: 1024px) {
    padding: 2rem 1rem;
    min-height: 40vh;
  }
}

.hero-content {
  max-width: 500px;
  text-align: center;
  animation: fadeInLeft 0.8s ease-out;
  
  @media (max-width: 1024px) {
    max-width: 400px;
  }
}

.hero-title {
  font-size: 4.5rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
}

.title-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-size: 4.5rem;
  font-weight: 800;
  margin-right: 0.5rem;
  display: block;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  letter-spacing: -0.02em;
}

.title-highlight {
  color: #333;
  font-size: 2.5rem;
  font-weight: 700;
  display: block;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-description {
  font-size: 1.25rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  
  strong {
    background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.8) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
  }
}

.hero-features {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  
  @media (max-width: 768px) {
    flex-direction: row;
    justify-content: center;
    flex-wrap: wrap;
  }
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1rem 1.5rem;
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateX(8px);
  }
  
  .feature-icon {
    font-size: 1.5rem;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  }
  
  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
    padding: 0.75rem;
    
    &:hover {
      transform: translateY(-4px);
    }
  }
}

// Form Section
.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  
  @media (max-width: 1024px) {
    padding: 2rem 1rem;
  }
}

.login-card {
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.15),
              0 0 0 1px rgba(255, 255, 255, 0.1);
  animation: fadeInRight 0.8s ease-out;
  
  @media (max-width: 768px) {
    padding: 2rem;
    max-width: 400px;
  }
}

.card-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.card-title {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 0.5rem;
  text-align: center;
}

.card-subtitle {
  color: #666;
  font-size: 1rem;
  text-align: center;
  margin-bottom: 2rem;
}

// Form Styles
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
  
  .label-icon {
    font-size: 1rem;
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
  }
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    background: rgba(255, 255, 255, 0.95);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
  }
  
  &::placeholder {
    color: #999;
  }
}

.input-border {
  position: absolute;
  inset: -2px;
  border-radius: 18px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  opacity: 0;
  z-index: -1;
  transition: opacity 0.3s ease;
}

.form-input:focus + .input-border {
  opacity: 1;
}

// Error Message
.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid rgba(255, 77, 79, 0.2);
  
  .error-icon {
    font-size: 1.1rem;
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
  }
}

// Login Button
.login-button {
  width: 100%;
  padding: 1.25rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.button-icon {
  font-size: 1.2rem;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-left: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// Form Footer
.form-footer {
  text-align: center;
}

.divider {
  position: relative;
  margin: 2rem 0;
  
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: rgba(0, 0, 0, 0.1);
  }
}

.divider-text {
  position: relative;
  padding: 0 1rem;
  color: #333;
  font-size: 0.9rem;
  font-weight: 500;
  background: transparent;
  z-index: 1;
}

.auth-links {
  display: flex;
  gap: 1rem;
  justify-content: center;
  
  @media (max-width: 480px) {
    flex-direction: column;
  }
}

.auth-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  
  &.primary {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
    color: #667eea;
    border: 1px solid rgba(102, 126, 234, 0.3);
    
    &:hover {
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.25), rgba(118, 75, 162, 0.25));
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);
    }
  }
  
  &.secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #666;
    border: 1px solid rgba(255, 255, 255, 0.2);
    
    &:hover {
      background: rgba(255, 255, 255, 0.2);
      color: #333;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }
  
  .link-icon {
    font-size: 1rem;
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
  }
}

// Animations
@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}
</style> 