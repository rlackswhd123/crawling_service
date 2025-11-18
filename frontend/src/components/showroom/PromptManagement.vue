<template>
  <Card class="mt-8">
    <Collapsible v-model:open="isOpen">
      <CollapsibleTrigger class="w-full">
        <CardHeader class="cursor-pointer transition-colors">
          <div class="flex items-center justify-between">
            <CardTitle class="flex items-center gap-2">
              📝 프롬프트 관리
              <Badge v-if="prompts.length > 0" variant="secondary">
                {{ prompts.length }}
              </Badge>
            </CardTitle>
            <svg
              class="w-5 h-5 transition-transform"
              :class="{ 'rotate-180': isOpen }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </CardHeader>
      </CollapsibleTrigger>

      <CollapsibleContent>
        <CardContent class="space-y-4">
          <!-- Refresh Button -->
          <div class="flex justify-end">
            <Button variant="outline" @click="loadPrompts" :disabled="isLoading" size="sm">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              새로고침
            </Button>
          </div>

          <!-- Loading State -->
          <div v-if="isLoading" class="text-center py-8 text-gray-500">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
            <p>프롬프트 목록을 불러오는 중...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="prompts.length === 0" class="text-center py-8 text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>저장된 프롬프트가 없습니다</p>
            <p class="text-sm mt-1">프롬프트를 작성하고 저장해보세요!</p>
          </div>

          <!-- Prompt List -->
          <div v-else class="space-y-2 max-h-96 overflow-y-auto">
            <PromptListItem
              v-for="prompt in prompts"
              :key="prompt.promptKey"
              :prompt-key="prompt.promptKey"
              :prompt-text="prompt.promptText"
              :cre-date="prompt.creDate || ''"
              :avg-rating="prompt.avgRating"
              :is-default-yn="prompt.isDefaultYn"
              @click="handlePromptClick"
              @rating-submitted="loadPrompts"
            />
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {{ errorMessage }}
          </div>
        </CardContent>
      </CollapsibleContent>
    </Collapsible>
  </Card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import PromptListItem from './PromptListItem.vue';
import { listPrompts } from '@/services/common/prompt.service';
import type { Prompt } from '@/types/prompt.types';

interface Props {
  modelValue: string;  // Current prompt text
  promptKind: string;  // e.g., "bangkku/video-generation"
}

interface Emits {
  (e: 'update:modelValue', value: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const isOpen = ref(false);
const isLoading = ref(false);
const prompts = ref<Prompt[]>([]);
const errorMessage = ref('');

onMounted(() => {
  loadPrompts();
});

const loadPrompts = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  try {
    prompts.value = await listPrompts({
      promptKind: props.promptKind,
      includeNonDefault: true,
    });
  } catch (error) {
    console.error('Failed to load prompts:', error);
    errorMessage.value = '프롬프트 목록을 불러오는데 실패했습니다.';
  } finally {
    isLoading.value = false;
  }
};

const handlePromptClick = (promptKey: number) => {
  const selectedPrompt = prompts.value.find(p => p.promptKey === promptKey);
  if (selectedPrompt) {
    emit('update:modelValue', selectedPrompt.promptText);
  }
};
</script>
