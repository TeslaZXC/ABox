<template>
  <div class="landing-container">
    <v-app-bar color="transparent" flat height="80" style="position: absolute; z-index: 100">
      <v-container class="d-flex align-center py-0">
        <v-toolbar-title class="font-weight-bold text-white d-flex align-center">
          <v-icon icon="mdi-cloud-outline" size="large" class="mr-2"></v-icon>
          ABox
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <div class="hidden-sm-and-down">
          <v-btn variant="text" color="white" class="mr-2" to="/login">Войти</v-btn>
          <v-btn color="white" class="glass-btn px-8 rounded-pill" to="/register">Начать</v-btn>
        </div>
      </v-container>
    </v-app-bar>

    <v-main class="pa-0">
      <section class="section hero-section position-relative overflow-hidden">
        <v-img src="/images/1.png" cover class="position-absolute fill-height w-100" style="z-index: 1; filter: brightness(0.4) blur(4px); transform: scale(1.1)"></v-img>
        <div class="position-absolute fill-height w-100" style="z-index: 2; background: radial-gradient(circle, transparent 0%, rgba(0,0,0,0.4) 100%)"></div>
        
        <v-container class="position-relative" style="z-index: 3">
          <v-row align="center" justify="center">
            <v-col cols="12" md="10" class="text-center">
              <h1 class="text-h1 font-weight-black text-white mb-6 tracking-tighter fade-in" style="text-shadow: 0 10px 30px rgba(0,0,0,0.5)">
                ABox
              </h1>
              <p class="text-h4 text-white mb-10 font-weight-light slide-up" style="text-shadow: 0 5px 15px rgba(0,0,0,0.5)">
                Ваше облачное пространство в стиле «жидкого стекла».
                <br/>
                Просто. Быстро. Красиво.
              </p>
              <div class="d-flex flex-column flex-sm-row justify-center ga-6 scale-in">
                <v-btn
                  size="x-large"
                  color="white"
                  class="glass-btn px-10 py-6 rounded-xl font-weight-bold text-h5"
                  to="/register"
                >
                  Начать использование
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <section class="section features-section">
        <v-container>
          <v-row>
            <v-col cols="12" class="text-center mb-16">
              <h2 class="text-h2 font-weight-bold text-white mb-4">Почему ABox?</h2>
            </v-col>
            <v-col cols="12" md="4" v-for="(feature, i) in features" :key="i">
              <v-card class="glass-card pa-8 h-100 text-center feature-card">
                <v-icon :icon="feature.icon" size="64" color="white" class="mb-6"></v-icon>
                <h3 class="text-h4 font-weight-bold text-white mb-4">{{ feature.title }}</h3>
                <p class="text-body-1 text-white opacity-80 leading-relaxed">
                  {{ feature.description }}
                </p>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <section class="section bucket-management-section px-6">
        <v-container>
          <v-row align="center" justify="space-between" class="ga-12">
            <v-col cols="12" md="5">
              <h2 class="text-h2 font-weight-black text-white mb-6 leading-tight">
                Взгляните на ABox
              </h2>
              <p class="text-h4 text-white opacity-90 mb-8 leading-relaxed font-weight-light">
                Вы можете создавать <span class="font-weight-bold">неограниченное количество бакетов</span> для любых ваших нужд.
              </p>
              <div class="d-flex align-center mb-4 text-white">
                <v-icon icon="mdi-check-circle" color="white" class="mr-3"></v-icon>
                <span>Полная изоляция данных между проектами</span>
              </div>
              <div class="d-flex align-center mb-4 text-white">
                <v-icon icon="mdi-check-circle" color="white" class="mr-3"></v-icon>
                <span>Управление квотами и доступом</span>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="browser-mockup slide-up">
                <div class="browser-header">
                  <div class="browser-dots">
                    <span class="dot red"></span>
                    <span class="dot yellow"></span>
                    <span class="dot green"></span>
                  </div>
                  <div class="browser-address">abox.cloud/disk</div>
                </div>
                <div class="browser-content">
                  <v-img src="/images/2.png" cover class="mockup-img"></v-img>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <section class="section viewer-section px-6 py-24">
        <v-container>
          <v-row align="center" justify="space-between" class="ga-12 flex-md-row-reverse">
            <v-col cols="12" md="5">
              <h2 class="text-h2 font-weight-black text-white mb-6 leading-tight">
                Встроенный вьювер
              </h2>
              <p class="text-h4 text-white opacity-90 mb-8 leading-relaxed font-weight-light">
                Для вашего удобства в ABox есть <span class="font-weight-bold">встроенный вьювер</span>.
              </p>
              <p class="text-body-1 text-white opacity-70 mb-8">
                Просматривайте фотографии, слушайте музыку и смотрите видео напрямую из облака без необходимости скачивания.
              </p>
              <v-btn variant="outlined" color="white" rounded="pill" size="large" class="px-8 border-2" prepend-icon="mdi-eye">
                Попробовать демо
              </v-btn>
            </v-col>
            <v-col cols="12" md="6">
              <div class="browser-mockup scale-in">
                <div class="browser-header">
                  <div class="browser-dots">
                    <span class="dot red"></span>
                    <span class="dot yellow"></span>
                    <span class="dot green"></span>
                  </div>
                  <div class="browser-address">abox.cloud/disk/viewer</div>
                </div>
                <div class="browser-content">
                  <v-img src="/images/3.png" cover class="mockup-img"></v-img>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <section class="section cta-section">
        <v-container class="text-center py-16">
          <v-card class="glass-card pa-16 d-inline-block max-w-4xl w-full">
            <h2 class="text-h2 font-weight-black text-white mb-6">Готовы расширить горизонты?</h2>
            <p class="text-h5 text-white opacity-80 mb-10 italic">
              «Будущее облачного хранения уже здесь. Оно прозрачное и легкое».
            </p>
            <div class="d-flex flex-column flex-sm-row justify-center ga-6">
              <v-btn size="x-large" color="white" class="glass-btn px-10 rounded-xl font-weight-bold" to="/register">
                Создать аккаунт
              </v-btn>
              <v-btn size="x-large" variant="outlined" color="white" class="px-10 rounded-xl font-weight-bold border-2" to="/login">
                Войти в кабинет
              </v-btn>
            </div>
          </v-card>
        </v-container>
        
        <v-footer color="transparent" class="text-white text-center d-flex flex-column pb-10">
          <div class="opacity-50 text-caption font-weight-light">
             &copy; 2026 ABox Storage Solutions. All rights reserved.
          </div>
        </v-footer>
      </section>
    </v-main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const features = [
  {
    icon: 'mdi-lightning-bolt',
    title: 'Скорость',
    description: 'Мгновенный доступ к вашим данным.'
  },
  {
    icon: 'mdi-glass-stange',
    title: 'Стиль',
    description: 'Уникальный интерфейс «жидкого стекла».'
  },
  {
    icon: 'mdi-shield-check',
    title: 'Защита',
    description: 'Ваши файлы под надежной охраной.'
  }
]
</script>

<style scoped>
.landing-container {
  overflow-y: auto;
  scroll-behavior: smooth;
  height: 100vh;
}

.section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 100px 0;
}

.hero-section {
  background: transparent;
}

.feature-card {
  transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.feature-card:hover {
  transform: translateY(-15px) scale(1.02);
}

.experience-list {
  list-style: none;
  padding: 0;
}

.pulse-icon {
  animation: pulse 3s infinite ease-in-out;
  filter: drop-shadow(0 0 30px rgba(255, 255, 255, 0.4));
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
}

.fade-in { animation: fadeIn 1s ease-out; }
.slide-up { animation: slideUp 1.2s ease-out; }
.scale-in { animation: scaleIn 0.8s ease-out; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes scaleIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.tracking-tighter {
  letter-spacing: -0.05em;
}

:deep(.v-footer) {
  margin-top: -100px;
}
.hero-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.browser-mockup {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4);
  width: 100%;
}

.browser-header {
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.browser-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.red { background: #ff5f56; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #27c93f; }

.browser-address {
  margin: 0 auto;
  font-size: 12px;
  color: white;
  opacity: 0.5;
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 20px;
  border-radius: 4px;
}

.browser-content {
  line-height: 0;
}

.mockup-img {
  width: 100%;
  transition: transform 1s ease;
}

.browser-mockup:hover .mockup-img {
  transform: scale(1.05);
}

@media (max-width: 960px) {
  .section {
    padding: 80px 0;
  }
}
</style>
