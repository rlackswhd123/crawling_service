<template>
  <aside
    class="fixed top-0 left-0 bg-gray-50 border-r border-gray-200 h-screen flex flex-col transition-all duration-300 z-40"
    :class="isCollapsed ? 'w-14' : 'w-64'"
  >
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200">
      <div v-if="!isCollapsed">
        <h1 class="text-xl font-bold text-gray-900">새움 AI</h1>
        <p class="text-sm text-gray-500">테스트공간</p>
      </div>
      <button
        @click="toggleCollapse"
        class="p-2 rounded-md hover:bg-gray-100 transition"
      >
        <span v-if="isCollapsed">➡️</span>
        <span v-else>⬅️</span>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-2 overflow-y-auto">
      <!-- 상품 쇼룸 Section -->
      <div class="mb-4">
        <Collapsible v-model:open="showroomOpen">
          <CollapsibleTrigger
            class="flex items-center justify-between w-full p-2 text-left hover:bg-gray-100 rounded-md"
            v-if="!isCollapsed"
          >
            <div class="flex items-center gap-2">
              <span class="text-lg">🎁</span>
              <span class="font-semibold text-gray-900">쇼룸</span>
            </div>
            <span class="text-gray-400 text-sm">{{ showroomOpen ? '▼' : '▶' }}</span>
          </CollapsibleTrigger>

          <!-- collapsed 상태일 때는 아이콘만 -->
          <button
            v-else
            @click="showroomOpen = !showroomOpen"
            class="flex items-center justify-center w-full p-2 hover:bg-gray-100 rounded-md"
          >
          🎁
          </button>

          <CollapsibleContent v-if="showroomOpen && !isCollapsed" class="mt-2 space-y-1 pl-6">
            <router-link
              v-for="item in showroomItems"
              :key="item.path"
              :to="item.path"
              class="flex items-center gap-2 p-2 text-sm rounded-md hover:bg-gray-100 transition-colors"
              :class="{ 'bg-blue-50 text-blue-700 font-medium': isActive(item.path) }"
            >
              <span>{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>
          </CollapsibleContent>
        </Collapsible>
      </div>

      <!-- 방꾸 Section -->
      <div class="mb-4">
        <Collapsible v-model:open="bangkkuOpen">
          <CollapsibleTrigger
            class="flex items-center justify-between w-full p-2 text-left hover:bg-gray-100 rounded-md"
            v-if="!isCollapsed"
          >
            <div class="flex items-center gap-2">
              <span class="text-lg">📦</span>
              <span class="font-semibold text-gray-900">방꾸</span>
            </div>
            <span class="text-gray-400 text-sm">{{ bangkkuOpen ? '▼' : '▶' }}</span>
          </CollapsibleTrigger>

          <!-- collapsed 상태일 때는 아이콘만 -->
          <button
            v-else
            @click="bangkkuOpen = !bangkkuOpen"
            class="flex items-center justify-center w-full p-2 hover:bg-gray-100 rounded-md"
          >
          📦
          </button>

          <CollapsibleContent v-if="bangkkuOpen && !isCollapsed" class="mt-2 space-y-1 pl-6">
            <router-link
              v-for="item in bangkkuItems"
              :key="item.path"
              :to="item.path"
              class="flex items-center gap-2 p-2 text-sm rounded-md hover:bg-gray-100 transition-colors"
              :class="{ 'bg-blue-50 text-blue-700 font-medium': isActive(item.path) }"
            >
              <span>{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>
          </CollapsibleContent>
        </Collapsible>
      </div>

      <!-- 헤어 Section -->
      <div class="mb-4">
        <Collapsible v-model:open="hairOpen">
          <CollapsibleTrigger
            class="flex items-center justify-between w-full p-2 text-left hover:bg-gray-100 rounded-md"
            v-if="!isCollapsed"
          >
            <div class="flex items-center gap-2">
              <span class="text-lg">💈</span>
              <span class="font-semibold text-gray-900">헤어</span>
            </div>
            <span class="text-gray-400 text-sm">{{ hairOpen ? '▼' : '▶' }}</span>
          </CollapsibleTrigger>

          <button
            v-else
            @click="hairOpen = !hairOpen"
            class="flex items-center justify-center w-full p-2 hover:bg-gray-100 rounded-md"
          >
            💈
          </button>

          <CollapsibleContent v-if="hairOpen && !isCollapsed" class="mt-2 space-y-1 pl-6">
            <router-link
              v-for="item in hairItems"
              :key="item.path"
              :to="item.path"
              class="flex items-center gap-2 p-2 text-sm rounded-md hover:bg-gray-100 transition-colors"
              :class="{ 'bg-blue-50 text-blue-700 font-medium': isActive(item.path) }"
            >
              <span>{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>
          </CollapsibleContent>
        </Collapsible>
      </div>

      <!-- 크롤링 Section -->
      <div class="mb-4">
        <Collapsible v-model:open="crawOpen">
          <CollapsibleTrigger
            class="flex items-center justify-between w-full p-2 text-left hover:bg-gray-100 rounded-md"
            v-if="!isCollapsed"
          >
            <div class="flex items-center gap-2">
              <span class="text-lg">🖥️</span>
              <span class="font-semibold text-gray-900">크롤링</span>
            </div>
            <span class="text-gray-400 text-sm">{{ crawOpen ? '▼' : '▶' }}</span>
          </CollapsibleTrigger>

          <button
            v-else
            @click="crawOpen = !crawOpen"
            class="flex items-center justify-center w-full p-2 hover:bg-gray-100 rounded-md"
          >
            💈
          </button>

          <CollapsibleContent v-if="crawOpen && !isCollapsed" class="mt-2 space-y-1 pl-6">
            <router-link
              v-for="item in crawItems"
              :key="item.path"
              :to="item.path"
              class="flex items-center gap-2 p-2 text-sm rounded-md hover:bg-gray-100 transition-colors"
              :class="{ 'bg-blue-50 text-blue-700 font-medium': isActive(item.path) }"
            >
              <span>{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>
          </CollapsibleContent>
        </Collapsible>
      </div>

      <!-- 애니톡 Section -->
      <div class="mb-4">
        <button
          v-if="!isCollapsed"
          @click="handleComingSoon('애니톡')"
          class="flex items-center justify-between w-full p-2 text-left hover:bg-gray-100 rounded-md opacity-60 cursor-not-allowed"
        >
          <div class="flex items-center gap-2">
            <span class="text-lg">📱</span>
            <span class="font-semibold text-gray-900">애니톡</span>
          </div>
          <Badge variant="secondary" class="text-xs">Soon</Badge>
        </button>

        <!-- Collapsed 모드에서는 아이콘만 -->
        <button
          v-else
          @click="handleComingSoon('애니톡')"
          class="flex items-center justify-center w-full p-2 hover:bg-gray-100 rounded-md opacity-60 cursor-not-allowed"
        >
          📱
        </button>
      </div>

      <!-- BAIK Section -->
      <div class="mb-4">
        <button
          v-if="!isCollapsed"
          @click="handleComingSoon('BAIK')"
          class="flex items-center justify-between w-full p-2 text-left hover:bg-gray-100 rounded-md opacity-60 cursor-not-allowed"
        >
          <div class="flex items-center gap-2">
            <span class="text-lg">🤖</span>
            <span class="font-semibold text-gray-900">BAIK</span>
          </div>
          <Badge variant="secondary" class="text-xs">Soon</Badge>
        </button>

        <button
          v-else
          @click="handleComingSoon('BAIK')"
          class="flex items-center justify-center w-full p-2 hover:bg-gray-100 rounded-md opacity-60 cursor-not-allowed"
        >
          🤖
        </button>
      </div>
    </nav>

    <!-- Footer -->
    <div
      class="p-4 border-t border-gray-200 text-xs text-gray-500"
      v-if="!isCollapsed"
    >
      © 2025 새움소프트
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Badge } from '@/components/ui/badge';

const route = useRoute();
const showroomOpen = ref(true);
const bangkkuOpen = ref(true);
const hairOpen = ref(true);
const crawOpen = ref(true);
const isCollapsed = ref(false);
const isMobile = ref(false);

const emit = defineEmits(['update:isCollapsed']);

const showroomItems = [
  { path: '/showroom/showroom-generator', label: '상품 쇼룸 생성', icon: '🖼️' }
];

const bangkkuItems = [
  { path: '/bangkku/furniture-removal', label: '가구 제거', icon: '🛋️' },
  { path: '/bangkku/furniture-front-view', label: '가구 드래그 이미지로 변환', icon: '🖼️' },
  { path: '/bangkku/3d-room-generator', label: '3D 룸 생성', icon: '🏠' },
  { path: '/bangkku/video-generation', label: '비디오 생성', icon: '🎬' },
];

const hairItems = [
  { path: '/hair/hair-generator', label: '헤어 스타일 생성', icon: '💈' },
  { path: '/hair/video-generation', label: '비디오 생성', icon: '🎬' },
];
const crawItems = [
  { path: '/craw/crawling', label: '공지사항 크롤링', icon: '🖥️' }
];

const isActive = (path: string) => route.path === path;

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
  emit('update:isCollapsed', isCollapsed.value);
};

const handleResize = () => {
  isMobile.value = window.innerWidth < 768;
  isCollapsed.value = isMobile.value;
  emit('update:isCollapsed', isCollapsed.value);
};

const handleComingSoon = (serviceName: string) => {
  alert(`${serviceName} 서비스는 준비 중입니다.`);
};

onMounted(() => {
  handleResize();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>
