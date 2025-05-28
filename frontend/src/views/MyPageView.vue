<script setup>
import { ref, onMounted } from 'vue';
import axiosInstance from '@/utils/axios';

// 사용자 정보 상태
const userInfo = ref({
  id: '',
  email: '',
  first_name: '',
  last_name: '',
  date_of_birth: '',
  created_at: '',
  updated_at: ''
});

const isLoading = ref(true);

// 비밀번호 변경 관련 상태
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});
const isPasswordChanging = ref(false);
const passwordChangeMessage = ref('');
const showPasswordForm = ref(false);

// 사용자 정보 가져오기
const fetchUserInfo = async () => {
  try {
    isLoading.value = true;
    const token = localStorage.getItem('access_token');
    if (!token) return;

    // localStorage에서 사용자 ID 가져오기
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = userData.id;
    
    if (!userId) {
      console.error('사용자 ID를 찾을 수 없습니다.');
      return;
    }

    // 백엔드 accounts/{id}/ 엔드포인트 호출
    const userResponse = await axiosInstance.get(`/accounts/${userId}/`);
    userInfo.value = userResponse.data.user;

  } catch (error) {
    console.error('사용자 정보 가져오기 실패:', error);
  } finally {
    isLoading.value = false;
  }
};

// 날짜 포맷팅
const formatDate = (dateString, dateOnly = false) => {
  if (!dateString) return '정보 없음';
  
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  };
  
  // 생년월일이 아닌 경우 시간도 포함
  if (!dateOnly) {
    options.hour = '2-digit';
    options.minute = '2-digit';
  }
  
  return new Date(dateString).toLocaleDateString('ko-KR', options);
};

// 비밀번호 변경 함수
const changePassword = async () => {
  // 유효성 검사
  if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    passwordChangeMessage.value = '모든 필드를 입력해주세요.';
    return;
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordChangeMessage.value = '새 비밀번호가 일치하지 않습니다.';
    return;
  }
  
  if (passwordForm.value.newPassword.length < 8) {
    passwordChangeMessage.value = '새 비밀번호는 8자 이상이어야 합니다.';
    return;
  }
  
  try {
    isPasswordChanging.value = true;
    passwordChangeMessage.value = '';
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      passwordChangeMessage.value = '로그인이 필요합니다.';
      return;
    }
    
    // localStorage에서 사용자 ID 가져오기
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = userData.id;
    
    if (!userId) {
      passwordChangeMessage.value = '사용자 정보를 찾을 수 없습니다.';
      return;
    }
    
    const response = await axiosInstance.put(`/accounts/${userId}/password/`, {
      current_password: passwordForm.value.currentPassword,
      new_password1: passwordForm.value.newPassword,
      new_password2: passwordForm.value.confirmPassword
    });
    
    passwordChangeMessage.value = '비밀번호가 성공적으로 변경되었습니다.';
    
    // 폼 초기화
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
    
    // 3초 후 폼 닫기
    setTimeout(() => {
      showPasswordForm.value = false;
      passwordChangeMessage.value = '';
    }, 3000);
    
  } catch (error) {
    console.error('비밀번호 변경 실패:', error);
    if (error.response?.status === 400) {
      passwordChangeMessage.value = '현재 비밀번호가 올바르지 않습니다.';
    } else if (error.response?.status === 404) {
      passwordChangeMessage.value = '사용자를 찾을 수 없습니다.';
    } else {
      passwordChangeMessage.value = '비밀번호 변경 중 오류가 발생했습니다.';
    }
  } finally {
    isPasswordChanging.value = false;
  }
};

// 비밀번호 폼 토글
const togglePasswordForm = () => {
  showPasswordForm.value = !showPasswordForm.value;
  if (!showPasswordForm.value) {
    // 폼 닫을 때 초기화
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
    passwordChangeMessage.value = '';
  }
};

onMounted(() => {
  fetchUserInfo();
});
</script>

<template>
  <div class="mypage">
    <!-- Hero Section -->
    <div class="mypage-hero">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-icon">👤</span>
          <span>개인 프로필</span>
        </div>
        <h1 class="hero-title">
          <span class="title-gradient">나의</span>
          <span class="title-highlight">마이페이지</span>
        </h1>
        <p class="hero-description">
          개인 정보를 관리하고<br>
          <strong>나만의 뉴스 활동</strong>을 확인하세요
        </p>
      </div>
      <div class="hero-visual">
        <div class="profile-avatar">
          <div class="avatar-circle">
            <span class="avatar-icon">👤</span>
          </div>
          <div class="avatar-glow"></div>
        </div>
      </div>
    </div>

    <div class="mypage-content">
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>사용자 정보를 불러오고 있습니다...</p>
      </div>

      <div v-else class="content-grid">
        <!-- 프로필 정보 카드 -->
        <div class="profile-card">
          <div class="card-header">
            <div class="card-title">
              <span class="card-icon">📝</span>
              <h2>프로필 정보</h2>
            </div>
          </div>

          <div class="profile-content">
            <div class="profile-display">
              <div class="profile-field">
                <label>사용자명 (이메일)</label>
                <div class="field-value">{{ userInfo.email || '이메일 정보 없음' }}</div>
              </div>
              <div class="profile-field">
                <label>이름</label>
                <div class="field-value">
                  {{ (userInfo.first_name && userInfo.last_name) 
                     ? `${userInfo.last_name}${userInfo.first_name}` 
                     : '이름 정보 없음' }}
                </div>
              </div>
              <div class="profile-field">
                <label>생년월일</label>
                <div class="field-value">{{ formatDate(userInfo.date_of_birth, true) }}</div>
              </div>
              <div class="profile-field">
                <label>가입일</label>
                <div class="field-value">{{ formatDate(userInfo.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 계정 관리 카드 -->
        <div class="account-card">
          <div class="card-header">
            <div class="card-title">
              <span class="card-icon">⚙️</span>
              <h2>계정 관리</h2>
            </div>
          </div>

          <div class="account-actions">
            <router-link to="/dashboard" class="action-button dashboard">
              <span class="action-icon">📊</span>
              <div class="action-content">
                <span class="action-title">대시보드</span>
                <span class="action-desc">상세한 활동 분석 및 통계 보기</span>
              </div>
            </router-link>
            
            <div @click="togglePasswordForm" class="action-button security">
              <span class="action-icon">🔐</span>
              <div class="action-content">
                <span class="action-title">비밀번호 변경</span>
                <span class="action-desc">안전하게 비밀번호 변경하기</span>
              </div>
            </div>
          </div>

          <!-- 비밀번호 변경 폼 -->
          <div v-if="showPasswordForm" class="password-form-section">
            <div class="password-form-header">
              <h3>비밀번호 변경</h3>
              <button @click="togglePasswordForm" class="close-button">
                <span>❌</span>
              </button>
            </div>
            
            <form @submit.prevent="changePassword" class="password-form">
              <div class="form-group">
                <label>현재 비밀번호</label>
                <input 
                  v-model="passwordForm.currentPassword" 
                  type="password" 
                  class="form-input"
                  placeholder="현재 비밀번호를 입력하세요"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>새 비밀번호</label>
                <input 
                  v-model="passwordForm.newPassword" 
                  type="password" 
                  class="form-input"
                  placeholder="새 비밀번호를 입력하세요 (8자 이상)"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>새 비밀번호 확인</label>
                <input 
                  v-model="passwordForm.confirmPassword" 
                  type="password" 
                  class="form-input"
                  placeholder="새 비밀번호를 다시 입력하세요"
                  required
                />
                <div v-if="passwordForm.confirmPassword && passwordForm.newPassword !== passwordForm.confirmPassword" class="error-message">
                  비밀번호가 일치하지 않습니다.
                </div>
              </div>
              
              <div v-if="passwordChangeMessage" class="message" :class="{ success: passwordChangeMessage.includes('성공'), error: !passwordChangeMessage.includes('성공') }">
                {{ passwordChangeMessage }}
              </div>
              
              <div class="password-form-actions">
                <button type="button" @click="togglePasswordForm" class="password-cancel-button">
                  <span>취소</span>
                </button>
                <button type="submit" :disabled="isPasswordChanging" class="password-save-button">
                  <div v-if="isPasswordChanging" class="loading-spinner small"></div>
                  <span v-else class="save-icon">🔒</span>
                  <span>{{ isPasswordChanging ? '변경 중...' : '비밀번호 변경' }}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.mypage {
  min-height: 100vh;
  padding-bottom: 4rem;
}

// Hero Section
.mypage-hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  margin-bottom: 4rem;
  padding: 2rem 0;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }
}

.hero-content {
  animation: fadeInUp 0.8s ease-out;
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
  font-size: 3.5rem;
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
}

.title-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-right: 1rem;
}

.title-highlight {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.25rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  
  strong {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
  }
}

.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
  animation: slideInRight 0.8s ease-out 0.2s both;
}

.profile-avatar {
  position: relative;
  width: 200px;
  height: 200px;
}

.avatar-circle {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 2;
  animation: float 3s ease-in-out infinite;
}

.avatar-icon {
  font-size: 4rem;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

.avatar-glow {
  position: absolute;
  inset: -4px;
  background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
  border-radius: 50%;
  opacity: 0.7;
  z-index: 1;
  filter: blur(12px);
  animation: pulse 2s infinite;
}

// Content Grid
.mypage-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    max-width: 600px;
  }
}

// Card Base Styles
.profile-card, .account-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 32px 64px rgba(0, 0, 0, 0.15);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  
  .card-icon {
    font-size: 1.5rem;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  }
  
  h2 {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
  }
}

// Profile Card
.profile-display {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-field {
  label {
    display: block;
    font-size: 0.9rem;
    font-weight: 600;
    color: #666;
    margin-bottom: 0.5rem;
  }
  
  .field-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
    padding: 0.75rem 1rem;
    background: rgba(0, 0, 0, 0.02);
    border-radius: 12px;
    border: 1px solid rgba(0, 0, 0, 0.05);
  }
}

// Account Card
.account-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 16px;
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-2px);
    background: rgba(0, 0, 0, 0.04);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
  
  .action-icon {
    font-size: 1.5rem;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  }
  
  .action-content {
    .action-title {
      display: block;
      font-size: 1.1rem;
      font-weight: 700;
      color: #333;
      margin-bottom: 0.25rem;
    }
    
    .action-desc {
      font-size: 0.9rem;
      color: #666;
    }
  }
  
  &.dashboard:hover .action-title {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  &.security:hover .action-title {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

// Password Form Section
.password-form-section {
  margin-top: 2rem;
  padding: 2rem;
  background: rgba(102, 126, 234, 0.03);
  border-radius: 20px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  animation: fadeInUp 0.3s ease-out;
  
  .form-group {
    margin-bottom: 1.5rem;
    
    label {
      display: block;
      font-size: 0.9rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 0.5rem;
    }
  }
  
  .form-input {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid rgba(102, 126, 234, 0.1);
    border-radius: 12px;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.8);
    box-sizing: border-box;
    
    &:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
      background: white;
    }
  }
}

.password-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  
  h3 {
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
  }
}

.close-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 0, 0, 0.1);
    transform: scale(1.1);
  }
  
  span {
    font-size: 0.9rem;
  }
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.password-form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.password-cancel-button, .password-save-button {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  
  &:hover {
    transform: translateY(-2px);
  }
}

.password-cancel-button {
  background: #f3f4f6;
  color: #666;
  
  &:hover {
    background: #e5e7eb;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.password-save-button {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  
  &:hover {
    box-shadow: 0 8px 25px rgba(34, 197, 94, 0.3);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
}

.password-strength {
  margin-top: 0.5rem;
  
  .strength-bar {
    width: 100%;
    height: 4px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 0.25rem;
  }
  
  .strength-fill {
    height: 100%;
    transition: all 0.3s ease;
    border-radius: 2px;
    
    &.strength-0, &.strength-1 {
      background: linear-gradient(135deg, #ef4444, #dc2626);
    }
    
    &.strength-2 {
      background: linear-gradient(135deg, #f97316, #ea580c);
    }
    
    &.strength-3 {
      background: linear-gradient(135deg, #eab308, #ca8a04);
    }
    
    &.strength-4 {
      background: linear-gradient(135deg, #22c55e, #16a34a);
    }
    
    &.strength-5 {
      background: linear-gradient(135deg, #10b981, #059669);
    }
  }
  
  .strength-text {
    font-size: 0.8rem;
    font-weight: 600;
    color: #666;
  }
}

.error-message {
  font-size: 0.8rem;
  color: #ef4444;
  margin-top: 0.25rem;
  font-weight: 500;
}

.message {
  padding: 1rem;
  border-radius: 12px;
  font-weight: 600;
  text-align: center;
  
  &.success {
    background: rgba(34, 197, 94, 0.1);
    color: #16a34a;
    border: 1px solid rgba(34, 197, 94, 0.2);
  }
  
  &.error {
    background: rgba(239, 68, 68, 0.1);
    color: #dc2626;
    border: 1px solid rgba(239, 68, 68, 0.2);
  }
}

.loading-spinner.small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-left: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

// Loading State
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  gap: 1rem;
  
  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(102, 126, 234, 0.1);
    border-left: 3px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  p {
    color: #667eea;
    font-weight: 600;
    font-size: 0.9rem;
  }
}

// Animations
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// Responsive Design
@media (max-width: 768px) {
  .mypage-content {
    padding: 0 1rem;
  }
  
  .profile-card, .account-card {
    padding: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .password-form-section {
    padding: 1.5rem;
  }
  
  .password-form-header {
    h3 {
      font-size: 1.1rem;
    }
  }
}
</style> 