import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/bangkku/furniture-removal'
    },
    // 쇼룸 (showRoom) Routes
    {
      path: '/showroom/showroom-generator',
      name: 'ShowroomGenerator',
      component: () => import('@/views/showroom/ShowroomGenerator.vue'),
      meta: { title: '쇼룸 생성' }
    },
    // 방꾸 (Bangkku) Routes
    {
      path: '/bangkku/furniture-removal',
      name: 'FurnitureRemoval',
      component: () => import('@/views/bangkku/FurnitureRemoval.vue'),
      meta: { title: '가구 제거' }
    },
    {
      path: '/bangkku/furniture-front-view',
      name: 'FurnitureFrontView',
      component: () => import('@/views/bangkku/FurnitureFrontView.vue'),
      meta: { title: '가구 드래그 이미지로 변환' }
    },
    {
      path: '/bangkku/3d-room-generator',
      name: 'Room3DGenerator',
      component: () => import('@/views/bangkku/Room3DGenerator.vue'),
      meta: { title: '3D 룸 생성' }
    },
    {
      path: '/bangkku/video-generation',
      name: 'VideoGeneration',
      component: () => import('@/views/bangkku/VideoGenerator.vue'),
      meta: { title: '비디오 생성' }
    },
    // 헤어 (Hair) Routes
    {
      path: '/hair/hair-generator',
      name: 'HairGenerator',
      component: () => import('@/views/hair/HairGenerator.vue'),
      meta: { title: '헤어 변환' }
    },
    {
      path: '/hair/video-generation',
      name: 'HairVideoGeneration',
      component: () => import('@/views/hair/VideoGenerator.vue'),
      meta: { title: '비디오 생성' }
    },

    // 크롤링 (Crawling) Routes
    {
      path: '/craw/crawling',
      name: 'Crawling',
      component: () => import('@/views/crawling/DomainsView.vue'),
      meta: { title: '크롤링' }
    },

    // 애니톡 (AniTalk) Routes - Coming Soon
    {
      path: '/anytalk/:pathMatch(.*)*',
      name: 'AniTalkComingSoon',
      component: () => import('@/views/ComingSoon.vue'),
      meta: { title: '애니톡 - Coming Soon', service: 'anytalk' }
    },
    // BAIK Routes - Coming Soon
    {
      path: '/baik/:pathMatch(.*)*',
      name: 'BAIKComingSoon',
      component: () => import('@/views/ComingSoon.vue'),
      meta: { title: 'BAIK - Coming Soon', service: 'baik' }
    },
    // 404 Not Found
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      redirect: '/'
    }
  ]
});

// Set page title based on route meta
router.beforeEach((to, from, next) => {
  const title = to.meta.title as string || '새움 AI 테스트공간';
  document.title = title;
  next();
});

export default router;
