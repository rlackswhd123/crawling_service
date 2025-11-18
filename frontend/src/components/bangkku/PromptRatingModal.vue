<template>
  <Dialog v-model:open="isOpen">
    <DialogContent class="sm:max-w-[500px]">
      <DialogHeader>
        <DialogTitle>프롬프트 평가</DialogTitle>
        <DialogDescription>
          이 프롬프트의 품질을 평가해주세요
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-4 py-4">
        <!-- Star Rating -->
        <div class="space-y-2">
          <label class="text-sm font-medium">별점</label>
          <div class="flex gap-2">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              @click="ratingScore = star"
              class="focus:outline-none transition-transform hover:scale-110"
            >
              <svg
                class="w-8 h-8"
                :class="star <= ratingScore ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                />
              </svg>
            </button>
          </div>
          <p v-if="ratingScore > 0" class="text-sm text-gray-600">
            {{ ratingLabels[ratingScore - 1] }}
          </p>
        </div>

        <!-- Comment -->
        <div class="space-y-2">
          <label class="text-sm font-medium">코멘트 (선택)</label>
          <Textarea
            v-model="ratingCmt"
            placeholder="이 프롬프트에 대한 의견을 작성해주세요..."
            rows="4"
          />
        </div>

        <!-- Tags -->
        <div class="space-y-2">
          <label class="text-sm font-medium">태그 (선택)</label>
          <div class="flex flex-wrap gap-2">
            <Badge
              v-for="tag in availableTags"
              :key="tag"
              :variant="selectedTags.includes(tag) ? 'default' : 'outline'"
              class="cursor-pointer"
              @click="toggleTag(tag)"
            >
              {{ tag }}
            </Badge>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="handleCancel">
          취소
        </Button>
        <Button @click="handleSubmit" :disabled="ratingScore === 0 || isSubmitting">
          {{ isSubmitting ? '제출 중...' : '평가 제출' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';

interface Props {
  open: boolean;
  promptKey: number;
}

interface Emits {
  (e: 'update:open', value: boolean): void;
  (e: 'submit', data: {
    ratingScore: number;
    ratingCmt?: string;
    tags: string[];
  }): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const isOpen = ref(props.open);
const ratingScore = ref(0);
const ratingCmt = ref('');
const selectedTags = ref<string[]>([]);
const isSubmitting = ref(false);

const ratingLabels = [
  '매우 불만족',
  '불만족',
  '보통',
  '만족',
  '매우 만족',
];

const availableTags = [
  '정확함',
  '창의적',
  '상세함',
  '간결함',
  '개선 필요',
  '빠름',
  '느림',
];

watch(() => props.open, (newVal) => {
  isOpen.value = newVal;
});

watch(isOpen, (newVal) => {
  emit('update:open', newVal);
  if (!newVal) {
    resetForm();
  }
});

const toggleTag = (tag: string) => {
  const index = selectedTags.value.indexOf(tag);
  if (index > -1) {
    selectedTags.value.splice(index, 1);
  } else {
    selectedTags.value.push(tag);
  }
};

const handleSubmit = () => {
  if (ratingScore.value === 0) return;

  emit('submit', {
    ratingScore: ratingScore.value,
    ratingCmt: ratingCmt.value || undefined,
    tags: selectedTags.value,
  });

  isOpen.value = false;
};

const handleCancel = () => {
  isOpen.value = false;
};

const resetForm = () => {
  ratingScore.value = 0;
  ratingCmt.value = '';
  selectedTags.value = [];
};
</script>
