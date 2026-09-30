import { createRouter, type RouterHistory } from 'vue-router';
import HomeView from './views/HomeView.vue';

export function makeRouter(history: RouterHistory) {
  return createRouter({
    history,
    routes: [
      { path: '/', component: HomeView },
      { path: '/:pathMatch(.*)*', redirect: '/' },
    ],
  });
}
