import { createPinia } from 'pinia';
import { createApp } from 'vue';
import { createWebHistory } from 'vue-router';
import App from './App.vue';
import { makeI18n } from './i18n';
import { makeRouter } from './router';
import './style.css';

createApp(App).use(createPinia()).use(makeI18n()).use(makeRouter(createWebHistory())).mount('#app');
