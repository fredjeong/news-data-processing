<script setup></script>

<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-brand">
        <div class="brand-logo">
          <span class="logo-icon">🚀</span>
          <span class="logo-text">SSAFYNEWS</span>
        </div>
        <p class="brand-description">
          AI가 만드는 개인화된 뉴스 경험
        </p>
      </div>
      
      <div class="footer-links">
        <div class="link-group">
          <h4 class="link-title">서비스</h4>
          <a href="#" class="footer-link">맞춤 뉴스</a>
          <a href="#" class="footer-link">대시보드</a>
          <a href="#" class="footer-link">AI 챗봇</a>
        </div>
        
        <div class="link-group">
          <h4 class="link-title">정보</h4>
          <a href="#" class="footer-link">이용약관</a>
          <a href="#" class="footer-link">개인정보처리방침</a>
          <a href="#" class="footer-link">고객지원</a>
        </div>
        
        <div class="link-group">
          <h4 class="link-title">연결</h4>
          <a href="#" class="footer-link">📧 문의하기</a>
          <a href="#" class="footer-link">📱 앱 다운로드</a>
          <a href="#" class="footer-link">🌟 피드백</a>
        </div>
      </div>
    </div>
    
    <div class="footer-bottom">
      <div class="footer-divider"></div>
      <div class="footer-copyright">
        <p>© 2025 SSAFY NEWS. All rights reserved.</p>
        <p class="made-with-love">Made with ❤️ by SSAFY Team</p>
      </div>
    </div>
  </footer>
</template>

<style scoped lang="scss">
.footer {
  margin-top: 8rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 32px 32px 0 0;
  overflow: hidden;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
  }
}

.footer-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 4rem;
  padding: 4rem 2rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 2rem;
    padding: 2rem 1rem 1rem;
  }
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.logo-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.5));
  animation: pulse 3s infinite;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  line-height: 1.5;
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

.link-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.link-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: 0;
    width: 30px;
    height: 2px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 1px;
  }
}

.footer-link {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 0.5rem 0;
  border-radius: 8px;
  position: relative;
  
  &:hover {
    color: white;
    transform: translateX(8px);
    
    &::before {
      content: '';
      position: absolute;
      left: -8px;
      top: 50%;
      transform: translateY(-50%);
      width: 4px;
      height: 4px;
      background: linear-gradient(135deg, #667eea, #764ba2);
      border-radius: 50%;
    }
  }
}

.footer-bottom {
  padding: 0 2rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    padding: 0 1rem 1rem;
  }
}

.footer-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  margin-bottom: 2rem;
}

.footer-copyright {
  text-align: center;
  
  p {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.9rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
  }
}

.made-with-love {
  font-size: 0.85rem !important;
  color: rgba(255, 255, 255, 0.5) !important;
  
  &:hover {
    color: rgba(255, 255, 255, 0.8) !important;
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
