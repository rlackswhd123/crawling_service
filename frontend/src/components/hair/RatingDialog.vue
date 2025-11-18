<script setup lang="ts">
import { ref, computed } from 'vue';
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
import { submitPromptRating } from '@/services/common/prompt.service';

interface Props {
  open: boolean;
  promptKey: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:open': [value: boolean];
  'rating-submitted': [];
}>();

const selectedRating = ref(0);
const hoveredRating = ref(0);
const comment = ref('');
const isSubmitting = ref(false);
const errorMessage = ref('');

const displayRating = computed(() => hoveredRating.value || selectedRating.value);

const handleStarClick = (rating: number) => {
  selectedRating.value = rating;
};

const handleStarHover = (rating: number) => {
  hoveredRating.value = rating;
};

const handleStarLeave = () => {
  hoveredRating.value = 0;
};

const handleClose = () => {
  if (!isSubmitting.value) {
    emit('update:open', false);
    // Reset form
    setTimeout(() => {
      selectedRating.value = 0;
      hoveredRating.value = 0;
      comment.value = '';
      errorMessage.value = '';
    }, 300);
  }
};

const handleSubmit = async () => {
  if (selectedRating.value === 0) {
    errorMessage.value = '별점을 선택해주세요.';
    return;
  }

  isSubmitting.value = true;
  errorMessage.value = '';

  try {
    await submitPromptRating({
      promptKey: props.promptKey,
      ratingScore: selectedRating.value,
      ratingCmt: comment.value || undefined
    });

    // Success
    emit('rating-submitted');
    handleClose();

    // Show success toast (optional - can be handled by parent)
    console.log('✅ 평가가 제출되었습니다!');
  } catch (error) {
    console.error('평가 제출 실패:', error);
    errorMessage.value = '평가 제출 중 오류가 발생했습니다.';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <Dialog :open="open" @update:open="handleClose">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>프롬프트 평가</DialogTitle>
        <DialogDescription>
          이 프롬프트가 얼마나 만족스러우신가요?
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-6 py-4">
        <!-- Star Rating -->
        <div class="flex flex-col items-center gap-3">
          <div class="flex gap-2">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              class="transition-all hover:scale-110 focus:outline-none"
              @click="handleStarClick(star)"
              @mouseenter="handleStarHover(star)"
              @mouseleave="handleStarLeave"
              :disabled="isSubmitting"
            >
              <!-- 채워진 별 -->
              <svg
                v-if="star <= displayRating"
                class="w-10 h-10 text-yellow-400"
                viewBox="0 0 24 24"
                fill="currentColor"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>

              <!-- 비어있는 별 -->
              <svg
                v-else
                class="w-10 h-10 text-gray-300"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </button>
          </div>
          <p class="text-sm text-gray-500">
            {{ selectedRating > 0 ? `${selectedRating}점 선택됨` : '별을 클릭하여 평가하세요' }}
          </p>
        </div>

        <!-- Comment -->
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700">
            코멘트 (선택사항)
          </label>
          <Textarea
            v-model="comment"
            placeholder="이 프롬프트에 대한 의견을 남겨주세요..."
            :disabled="isSubmitting"
            rows="3"
            class="resize-none"
          />
        </div>

        <!-- Error Message -->
        <p v-if="errorMessage" class="text-sm text-red-600">
          {{ errorMessage }}
        </p>
      </div>

      <DialogFooter>
        <Button
          variant="outline"
          @click="handleClose"
          :disabled="isSubmitting"
        >
          취소
        </Button>
        <Button
          @click="handleSubmit"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? '제출 중...' : '평가 제출' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
