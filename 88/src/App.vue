<template>
  <div class="app-container">
    <header class="header">
      <div class="logo">
        <div class="logo-icon">
          <span class="lightning">⚡</span>
        </div>
        <div class="logo-text">
          <h1>涨停先知</h1>
          <span class="subtitle">ZTB Seer - 智能牛股分析系统</span>
        </div>
      </div>
      <nav class="nav">
        <router-link to="/" class="nav-link">
          <span class="nav-icon">🏠</span>
          首页
        </router-link>
        <router-link to="/stocks" class="nav-link">
          <span class="nav-icon">📊</span>
          行情
        </router-link>
      </nav>
    </header>
    <main class="main">
      <router-view />
    </main>
    <footer class="footer">
      <div class="footer-content">
        <p>⚡ 涨停先知 - 让每一次涨停都不再错过</p>
        <p class="disclaimer">免责声明：本系统仅供学习参考，不构成投资建议</p>
      </div>
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  min-height: 100vh;
  color: #fff;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  box-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.lightning {
  animation: flash 1.5s ease-in-out infinite;
}

@keyframes flash {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.logo-text h1 {
  color: #ffd700;
  font-size: 1.8rem;
  font-weight: 700;
  text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
  letter-spacing: 3px;
}

.subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.75rem;
  letter-spacing: 1px;
}

.nav {
  display: flex;
  gap: 1rem;
}

.nav-link {
  text-decoration: none;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  padding: 0.6rem 1.2rem;
  border-radius: 25px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-link:hover,
.nav-link.router-link-active {
  background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%);
  color: white;
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(255, 215, 0, 0.3);
}

.nav-icon {
  font-size: 1.1rem;
}

.main {
  flex: 1;
  padding: 2rem;
}

.footer {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem 2rem;
  text-align: center;
}

.footer-content p:first-child {
  color: #ffd700;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.disclaimer {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .logo-text h1 {
    font-size: 1.5rem;
  }
  
  .nav {
    width: 100%;
    justify-content: center;
  }
}
</style>
