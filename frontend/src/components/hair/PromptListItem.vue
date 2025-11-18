<template>
  <div
    class="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
    :class="{
      'border-2 border-blue-400 bg-blue-50': isDefaultYn === 1
    }"
    @click="handleClick"
  >
    <div class="flex justify-between items-start mb-2">
      <div class="flex-1">
        <p class="text-sm text-gray-600 line-clamp-2">
          <span v-if="isDefaultYn === 1" class="text-yellow-500">⭐ </span>{{ promptText }}
        </p>
      </div>

      <!-- Action Section -->
      <div class="flex items-center gap-2 ml-4">
        <!-- Average Rating (simplified) -->
        <span v-if="avgRating" class="text-sm text-yellow-500 font-medium">
          {{ avgRating.toFixed(1) }}⭐
        </span>

        <!-- Use Button -->
        <Button
          variant="default"
          size="sm"
          class="h-7 px-3 text-xs"
          @click.stop="handleUsePrompt"
        >
          사용하기
        </Button>

        <!-- Detail Button -->
        <Button
          variant="outline"
          size="sm"
          class="h-7 px-3 text-xs"
          @click.stop="handleShowDetail"
        >
          상세보기
        </Button>
      </div>
    </div>

    <div class="flex justify-between items-center text-xs text-gray-500">
      <span>{{ formatDate(creDate) }}</span>
      <span v-if="executionTimeMs">{{ executionTimeMs }}ms</span>
    </div>
  </div>

  <!-- Prompt Detail Dialog -->
  <PromptDetailDialog
    v-model:open="showDetailDialog"
    :prompt-key="promptKey"
    @data-updated="handleDetailDataUpdated"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Button } from '@/components/ui/button';
import PromptDetailDialog from './PromptDetailDialog.vue';

interface Props {
  promptKey: number;
  promptText: string;
  creDate: string;
  executionTimeMs?: number;
  avgRating?: number;
  isDefaultYn?: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  click: [promptKey: number];
  ratingSubmitted: [];
}>();

const showDetailDialog = ref(false);

const handleClick = () => {
  // Open detail dialog on card click
  showDetailDialog.value = true;
};

const handleUsePrompt = () => {
  // Set prompt to editor (restore original behavior)
  emit('click', props.promptKey);
};

const handleShowDetail = () => {
  // Open detail dialog
  showDetailDialog.value = true;
};

const handleDetailDataUpdated = () => {
  // When data is updated in detail dialog, notify parent to refresh
  emit('ratingSubmitted');
};

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  const now = new Date();
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

  if (diffInHours < 1) {
    return '방금 전';
  } else if (diffInHours < 24) {
    return `${diffInHours}시간 전`;
  } else if (diffInHours < 48) {
    return '어제';
  } else {
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
};
</script>
