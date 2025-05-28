<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import StateButton from "@/common/StateButton.vue";
import { authAPI } from "@/utils/api";
import { useValidation } from "@/composables/useValidation";

const router = useRouter();
const { validatePwd } = useValidation();

const email = ref("");
const firstName = ref("");
const lastName = ref("");
const dateOfBirth = ref("");
const password1 = ref("");
const password2 = ref("");
const error = ref("");
const isLoading = ref(false);

const register = async () => {
  isLoading.value = true;
  error.value = "";
  
  try {
    // 비밀번호 확인
    if (password1.value !== password2.value) {
      error.value = "비밀번호가 일치하지 않습니다.";
      isLoading.value = false;
      return;
    }

    // 비밀번호 검증
    const pwdError = validatePwd(password1.value);
    if (pwdError) {
      error.value = pwdError;
      isLoading.value = false;
      return;
    }

    // 필수 필드 검증
    if (!email.value || !firstName.value || !lastName.value || !dateOfBirth.value) {
      error.value = "모든 필드를 입력해주세요.";
      isLoading.value = false;
      return;
    }

    // authAPI를 사용하여 회원가입 요청
    const response = await authAPI.register({
      email: email.value,
      first_name: firstName.value,
      last_name: lastName.value,
      date_of_birth: dateOfBirth.value,
      password1: password1.value,
      password2: password2.value,
    });

    // JWT 토큰 저장
    if (response.data.access) {
      localStorage.setItem("access_token", response.data.access);
      localStorage.setItem("refresh_token", response.data.refresh);
      
      // 사용자 정보 저장
      if (response.data.user) {
        localStorage.setItem("user", JSON.stringify(response.data.user));
      }
      
      // 성공 메시지 처리
      console.log(response.data.message || "회원가입이 성공적으로 완료되었습니다.");
      
      // 회원가입 성공 시 메인 페이지로 이동
      router.push("/");
    } else {
      // JWT 토큰이 없는 경우 로그인 페이지로 이동
      router.push("/login");
    }
  } catch (err) {
    console.error("Registration error:", err);
    
    if (err.response && err.response.data) {
      if (typeof err.response.data === 'object') {
        if (err.response.data.message) {
          error.value = err.response.data.message;
        } else if (err.response.data.detail) {
          error.value = err.response.data.detail;
        } else if (err.response.data.non_field_errors) {
          error.value = err.response.data.non_field_errors[0];
        } else {
          // 필드별 에러 메시지 처리
          const errorMessages = [];
          for (const [field, messages] of Object.entries(err.response.data)) {
            if (Array.isArray(messages)) {
              errorMessages.push(`${field}: ${messages.join(", ")}`);
            } else {
              errorMessages.push(`${field}: ${messages}`);
            }
          }
          error.value = errorMessages.join("\n");
        }
      } else {
        error.value = "회원가입에 실패했습니다. 잠시 후 다시 시도해주세요.";
      }
    } else {
      error.value = "회원가입에 실패했습니다. 잠시 후 다시 시도해주세요.";
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="register-page">
    <!-- Hero Background -->
    <div class="hero-background">
      <div class="floating-elements">
        <div class="floating-element element-1">✨</div>
        <div class="floating-element element-2">🚀</div>
        <div class="floating-element element-3">💎</div>
        <div class="floating-element element-4">🌟</div>
        <div class="floating-element element-5">🎯</div>
        <div class="floating-element element-6">🔮</div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="register-container">
      <!-- Left Side - Hero Content -->
      <div class="hero-section">
        <div class="hero-content">
          <div class="hero-badge">
            <span class="badge-icon">✨</span>
            <span>새로운 시작</span>
          </div>
          <h1 class="hero-title">
            <span class="title-gradient">당신만의</span>
            <span class="title-highlight">뉴스 여정을</span>
            <span class="title-accent">시작하세요!</span>
          </h1>
          <p class="hero-description">
            AI가 분석하는 <strong>개인화된 뉴스</strong>로<br>
            더 스마트한 정보 소비를 경험해보세요
          </p>
          <div class="hero-benefits">
            <div class="benefit-item">
              <span class="benefit-icon">🤖</span>
              <div class="benefit-content">
                <h3>AI 맞춤 추천</h3>
                <p>당신의 관심사를 학습하여 최적의 뉴스를 추천</p>
              </div>
            </div>
            <div class="benefit-item">
              <span class="benefit-icon">📊</span>
              <div class="benefit-content">
                <h3>개인 대시보드</h3>
                <p>읽기 패턴과 관심 분야를 시각적으로 분석</p>
              </div>
            </div>
            <div class="benefit-item">
              <span class="benefit-icon">❤️</span>
              <div class="benefit-content">
                <h3>스마트 큐레이션</h3>
                <p>좋아요와 즐겨찾기로 나만의 뉴스 컬렉션</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Register Form -->
      <div class="form-section">
        <div class="register-card">
          <div class="card-header">
            <h2 class="card-title">회원가입</h2>
            <p class="card-subtitle">몇 가지 정보만 입력하면 바로 시작할 수 있어요</p>
          </div>

          <form @submit.prevent="register" class="register-form">
            <div class="form-row">
              <div class="input-group">
                <label for="firstName" class="input-label">
                  <span class="label-icon">👤</span>
                  이름
                </label>
                <div class="input-wrapper">
                  <input
                    type="text"
                    id="firstName"
                    v-model="firstName"
                    placeholder="이름을 입력하세요"
                    class="form-input"
                    required
                  />
                  <div class="input-border"></div>
                </div>
              </div>

              <div class="input-group">
                <label for="lastName" class="input-label">
                  <span class="label-icon">👥</span>
                  성
                </label>
                <div class="input-wrapper">
                  <input
                    type="text"
                    id="lastName"
                    v-model="lastName"
                    placeholder="성을 입력하세요"
                    class="form-input"
                    required
                  />
                  <div class="input-border"></div>
                </div>
              </div>
            </div>

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
              <label for="dateOfBirth" class="input-label">
                <span class="label-icon">🎂</span>
                생년월일
              </label>
              <div class="input-wrapper">
                <input
                  type="date"
                  id="dateOfBirth"
                  v-model="dateOfBirth"
                  class="form-input"
                  required
                />
                <div class="input-border"></div>
              </div>
            </div>

            <div class="input-group">
              <label for="password1" class="input-label">
                <span class="label-icon">🔒</span>
                비밀번호
              </label>
              <div class="input-wrapper">
                <input
                  type="password"
                  id="password1"
                  v-model="password1"
                  placeholder="비밀번호를 입력하세요"
                  class="form-input"
                  required
                />
                <div class="input-border"></div>
              </div>
              <div class="input-help">
                <span class="help-icon">💡</span>
                8자 이상, 숫자와 한글/영문을 포함해야 합니다
              </div>
            </div>

            <div class="input-group">
              <label for="password2" class="input-label">
                <span class="label-icon">🔐</span>
                비밀번호 확인
              </label>
              <div class="input-wrapper">
                <input
                  type="password"
                  id="password2"
                  v-model="password2"
                  placeholder="비밀번호를 다시 입력하세요"
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
              class="register-button"
              :loading="isLoading"
            >
              <span v-if="!isLoading" class="button-content">
                <span class="button-icon">🚀</span>
                회원가입하고 시작하기
              </span>
              <span v-else class="button-content">
                <span class="loading-spinner"></span>
                계정 생성 중...
              </span>
            </StateButton>
          </form>

          <div class="form-footer">
            <div class="divider">
              <span class="divider-text">이미 계정이 있으신가요?</span>
            </div>
            <div class="auth-links">
              <router-link to="/login" class="auth-link primary">
                <span class="link-icon">🔐</span>
                로그인하기
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.register-page {
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
    #764ba2 20%,
    #f093fb 40%,
    #f5576c 60%,
    #4facfe 80%,
    #00f2fe 100%
  );
  z-index: -1;
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(
      circle at 30% 70%,
      rgba(120, 119, 198, 0.3),
      transparent 50%
    ),
    radial-gradient(
      circle at 70% 30%,
      rgba(255, 119, 198, 0.3),
      transparent 50%
    ),
    radial-gradient(
      circle at 50% 50%,
      rgba(79, 172, 254, 0.2),
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
  animation: float 8s ease-in-out infinite;
  
  &.element-1 {
    top: 10%;
    left: 10%;
    animation-delay: 0s;
  }
  
  &.element-2 {
    top: 20%;
    right: 20%;
    animation-delay: 1.5s;
  }
  
  &.element-3 {
    bottom: 30%;
    left: 15%;
    animation-delay: 3s;
  }
  
  &.element-4 {
    bottom: 20%;
    right: 10%;
    animation-delay: 4.5s;
  }
  
  &.element-5 {
    top: 50%;
    left: 50%;
    animation-delay: 6s;
  }
  
  &.element-6 {
    top: 70%;
    right: 30%;
    animation-delay: 7.5s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg) scale(1);
  }
  33% {
    transform: translateY(-15px) rotate(120deg) scale(1.1);
  }
  66% {
    transform: translateY(-30px) rotate(240deg) scale(0.9);
  }
}

// Main Container
.register-container {
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
    min-height: 50vh;
  }
}

.hero-content {
  max-width: 550px;
  text-align: center;
  animation: fadeInLeft 0.8s ease-out;
  
  @media (max-width: 1024px) {
    max-width: 450px;
  }
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.badge-icon {
  font-size: 1.2rem;
  animation: pulse 2s infinite;
}

.hero-title {
  font-size: 3.2rem;
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  
  @media (max-width: 768px) {
    font-size: 2.2rem;
  }
}

.title-gradient {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
}

.title-highlight {
  background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
}

.title-accent {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
}

.hero-description {
  font-size: 1.2rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2.5rem;
  
  strong {
    background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.8) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
  }
}

.hero-benefits {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  text-align: left;
  
  @media (max-width: 768px) {
    text-align: center;
  }
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateX(8px);
  }
  
  .benefit-icon {
    font-size: 2rem;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    margin-top: 0.25rem;
  }
  
  .benefit-content {
    flex: 1;
    
    h3 {
      font-size: 1.1rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      color: rgba(255, 255, 255, 0.95);
    }
    
    p {
      font-size: 0.9rem;
      line-height: 1.4;
      color: rgba(255, 255, 255, 0.8);
      margin: 0;
    }
  }
  
  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
    
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

.register-card {
  width: 100%;
  max-width: 500px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.1);
  animation: fadeInRight 0.8s ease-out;
  
  @media (max-width: 768px) {
    padding: 2rem;
    max-width: 450px;
  }
}

.card-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.card-title {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.card-subtitle {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
}

// Form Styles
.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
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
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    background: rgba(255, 255, 255, 0.95);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
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

.input-help {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #666;
  background: rgba(102, 126, 234, 0.05);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border-left: 3px solid #667eea;
  
  .help-icon {
    font-size: 0.9rem;
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
  }
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
  white-space: pre-line;
  
  .error-icon {
    font-size: 1.1rem;
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
  }
}

// Register Button
.register-button {
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
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.3);
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
  background: rgba(255, 255, 255, 0.95);
  padding: 0 1rem;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
}

.auth-links {
  display: flex;
  justify-content: center;
}

.auth-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 2rem;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  
  &.primary {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    color: #667eea;
    border: 1px solid rgba(102, 126, 234, 0.2);
    
    &:hover {
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
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