<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <Sidebar :is-collapsed="isCollapsed" @update:isCollapsed="isCollapsed = $event" />

    <!-- Main Content -->
    <main
      class="flex-1 overflow-y-auto bg-white transition-all duration-300"
      :class="isCollapsed ? 'ml-14' : 'ml-64'"
    >
      <router-view />
    </main>
  </div>

  <!-- Toast Notifications -->
  <Toaster position="top-center" :rich-colors="true" :close-button="true" />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Sidebar from '@/components/layout/Sidebar.vue';
import { Toaster } from '@/components/ui/sonner';

const isCollapsed = ref(false);
</script>
