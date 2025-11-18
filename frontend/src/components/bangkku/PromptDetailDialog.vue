<template>
  <Dialog :open="open" @update:open="handleClose">
    <DialogContent class="sm:max-w-3xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          프롬프트 상세
          <Badge v-if="prompt?.promptKind" variant="outline" class="text-xs">
            {{ prompt.promptKind }}
          </Badge>
          <Badge v-if="prompt?.isDefaultYn === 1" variant="secondary" class="bg-yellow-100 text-yellow-800 text-xs">
            ⭐ 기본
          </Badge>
        </DialogTitle>
        <DialogDescription>
          프롬프트 정보, 통계, 평가 내역을 확인할 수 있습니다.
        </DialogDescription>
      </DialogHeader>

      <!-- Loading State -->
      <div v-if="isLoading" class="space-y-4 py-4">
        <Skeleton class="h-20 w-full" />
        <Skeleton class="h-20 w-full" />
        <Skeleton class="h-20 w-full" />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
        {{ error }}
      </div>

      <!-- Content -->
      <div v-else class="space-y-3">
        <!-- Section 1: 프롬프트 정보 -->
        <Collapsible v-model:open="sections.info">
          <CollapsibleTrigger class="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <span class="font-medium">프롬프트 정보</span>
            <svg
              class="w-5 h-5 transition-transform"
              :class="{ 'rotate-180': sections.info }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </CollapsibleTrigger>
          <CollapsibleContent class="p-4 space-y-3">
            <!-- Prompt Text -->
            <div>
              <label class="text-sm font-medium text-gray-700">프롬프트 텍스트</label>
              <div class="mt-1 p-3 bg-gray-50 rounded-lg border border-gray-200 max-h-40 overflow-y-auto">
                <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ prompt?.promptText }}</p>
              </div>
            </div>

            <!-- Model Kind -->
            <div v-if="prompt?.modelKind">
              <label class="text-sm font-medium text-gray-700">모델 종류</label>
              <p class="text-sm text-gray-600">{{ prompt.modelKind }}</p>
            </div>

            <!-- Dates -->
            <div class="grid grid-cols-2 gap-4">
              <div v-if="prompt?.creDate">
                <label class="text-sm font-medium text-gray-700">생성일시</label>
                <p class="text-sm text-gray-600">{{ formatDateTime(prompt.creDate) }}</p>
              </div>
              <div v-if="prompt?.updDate">
                <label class="text-sm font-medium text-gray-700">수정일시</label>
                <p class="text-sm text-gray-600">{{ formatDateTime(prompt.updDate) }}</p>
              </div>
            </div>

            <!-- Input Images -->
            <div v-if="prompt?.inputImages && prompt.inputImages.length > 0">
              <label class="text-sm font-medium text-gray-700">입력 이미지</label>
              <div class="mt-2 grid grid-cols-3 gap-2">
                <img
                  v-for="(imageUrl, idx) in prompt.inputImages"
                  :key="idx"
                  :src="getImageUrl(imageUrl)"
                  class="w-full h-24 object-contain rounded border"
                  alt="입력 이미지"
                />
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>

        <!-- Section 2: 통계 정보 -->
        <!-- TODO: 통계 정보 섹션 - 추후 구현 예정
        <Collapsible v-if="promptStats" v-model:open="sections.stats">
          <CollapsibleTrigger class="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <span class="font-medium">통계 정보</span>
            <svg
              class="w-5 h-5 transition-transform"
              :class="{ 'rotate-180': sections.stats }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </CollapsibleTrigger>
          <CollapsibleContent class="p-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-700">사용 횟수</label>
                <p class="text-lg font-semibold text-gray-900">{{ promptStats.useCnt }}회</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-700">성공 횟수</label>
                <p class="text-lg font-semibold text-gray-900">
                  {{ promptStats.successCnt }}회
                  <span class="text-sm text-gray-600">({{ successRate }}%)</span>
                </p>
              </div>
              <div v-if="promptStats.avgExecutionTime">
                <label class="text-sm font-medium text-gray-700">평균 실행시간</label>
                <p class="text-lg font-semibold text-gray-900">{{ promptStats.avgExecutionTime.toFixed(0) }}ms</p>
              </div>
              <div v-if="promptStats.avgTokenCnt">
                <label class="text-sm font-medium text-gray-700">평균 토큰</label>
                <p class="text-lg font-semibold text-gray-900">{{ promptStats.avgTokenCnt.toFixed(0) }} tokens</p>
              </div>
              <div v-if="promptStats.totalCost">
                <label class="text-sm font-medium text-gray-700">총 비용</label>
                <p class="text-lg font-semibold text-gray-900">${{ promptStats.totalCost.toFixed(2) }}</p>
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>
        -->

        <!-- Section 3: 평가 정보 -->
        <Collapsible v-if="statistics || ratings.length > 0" v-model:open="sections.ratings">
          <CollapsibleTrigger class="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <span class="font-medium">평가 정보 ({{ statistics?.totalRatings || ratings.length || 0 }}개)</span>
            <svg
              class="w-5 h-5 transition-transform"
              :class="{ 'rotate-180': sections.ratings }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </CollapsibleTrigger>
          <CollapsibleContent class="p-4 space-y-4">
            <!-- Average Rating -->
            <div v-if="statistics && statistics.avgRating != null" class="flex items-center gap-2">
              <div class="flex items-center text-yellow-500">
                <svg
                  v-for="star in 5"
                  :key="star"
                  class="w-5 h-5"
                  :class="star <= Math.round(statistics.avgRating) ? 'fill-current' : 'fill-none stroke-current'"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                </svg>
              </div>
              <span class="text-lg font-semibold">{{ statistics.avgRating.toFixed(1) }}</span>
              <span class="text-sm text-gray-600">(총 {{ statistics.totalRatings }}개)</span>
            </div>

            <!-- Rating Distribution -->
            <div v-if="statistics?.ratingDistribution" class="text-sm text-gray-600">
              <span class="font-medium">평점 분포:</span>
              <span class="ml-2">
                5점: {{ statistics.ratingDistribution['5'] || 0 }}개 |
                4점: {{ statistics.ratingDistribution['4'] || 0 }}개 |
                3점: {{ statistics.ratingDistribution['3'] || 0 }}개 |
                2점: {{ statistics.ratingDistribution['2'] || 0 }}개 |
                1점: {{ statistics.ratingDistribution['1'] || 0 }}개
              </span>
            </div>

            <!-- Individual Ratings List -->
            <div v-if="ratings.length > 0">
              <label class="text-sm font-medium text-gray-700 mb-2 block">개별 평가 목록</label>
              <div class="space-y-3 max-h-60 overflow-y-auto">
                <div
                  v-for="rating in ratings"
                  :key="rating.ratingKey"
                  class="p-3 border rounded-lg bg-gray-50 relative"
                >
                  <!-- Delete Button -->
                  <Button
                    variant="ghost"
                    size="sm"
                    class="absolute top-2 right-2 h-6 w-6 p-0 text-gray-400 hover:text-red-600"
                    @click="handleDeleteRating(rating.ratingKey)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </Button>

                  <!-- Rating Stars -->
                  <div class="flex items-center gap-1 text-yellow-500">
                    <svg
                      v-for="star in rating.ratingScore"
                      :key="star"
                      class="w-4 h-4 fill-current"
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                  </div>

                  <!-- Comment -->
                  <p v-if="rating.ratingCmt" class="text-sm text-gray-700 mt-2">
                    {{ rating.ratingCmt }}
                  </p>

                  <!-- Date -->
                  <span class="text-xs text-gray-500 mt-2 block">
                    {{ formatDate(rating.creDate || '') }}
                  </span>
                </div>
              </div>
            </div>

            <!-- No Ratings Message -->
            <div v-else class="text-center py-4 text-sm text-gray-500">
              아직 평가가 없습니다.
            </div>
          </CollapsibleContent>
        </Collapsible>
      </div>

      <!-- Dialog Footer -->
      <DialogFooter class="flex gap-2">
        <Button variant="default" @click="showRatingDialog = true">
          평가하기
        </Button>
        <Button
          v-if="prompt?.isDefaultYn !== 1"
          variant="outline"
          @click="handleSetAsDefault"
        >
          ⭐ 기본 설정
        </Button>
        <Button variant="destructive" @click="showDeleteDialog = true">
          삭제
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <!-- Rating Dialog -->
  <RatingDialog
    v-model:open="showRatingDialog"
    :prompt-key="promptKey"
    @rating-submitted="handleRatingSubmitted"
  />

  <!-- Delete Confirm Dialog -->
  <DeleteConfirmDialog
    v-model:open="showDeleteDialog"
    :prompt-text="prompt?.promptText || ''"
    @confirm="handleDeleteConfirm"
  />
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'vue-sonner';
import { getImageUrl } from '@/utils/image.utils';
import RatingDialog from './RatingDialog.vue';
import DeleteConfirmDialog from './DeleteConfirmDialog.vue';
import {
  getPrompt,
  getRatingsByPrompt,
  getPromptStatistics,
  getAverageRating,
  setAsDefaultPrompt,
  deletePrompt,
  deleteRating,
} from '@/services/common/prompt.service';
import type { Prompt, PromptRating, RatingStatistics, PromptStatistics } from '@/types/prompt.types';

interface Props {
  open: boolean;
  promptKey: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:open': [value: boolean];
  'data-updated': [];
}>();

// State
const isLoading = ref(true);
const error = ref('');

// Data
const prompt = ref<Prompt | null>(null);
const ratings = ref<PromptRating[]>([]);
const statistics = ref<RatingStatistics | null>(null);
const promptStats = ref<PromptStatistics | null>(null);

// Sub-dialogs
const showRatingDialog = ref(false);
const showDeleteDialog = ref(false);

// Accordion sections (default: info section open)
const sections = ref({
  info: true,
  stats: false,
  ratings: false,
});

// Computed
const successRate = computed(() => {
  if (!promptStats.value || promptStats.value.useCnt === 0) return 0;
  return ((promptStats.value.successCnt / promptStats.value.useCnt) * 100).toFixed(1);
});

// Load prompt details
const loadDetails = async () => {
  isLoading.value = true;
  error.value = '';

  try {
    // Parallel API calls for performance
    const [promptData, ratingsData, statsData, ratingStatsData] = await Promise.all([
      getPrompt(props.promptKey),
      getRatingsByPrompt(props.promptKey, 20).catch(() => []), // Ratings may not exist
      getPromptStatistics(props.promptKey).catch(() => null), // Stats may not exist
      getAverageRating(props.promptKey).catch(() => null), // Rating stats may not exist
    ]);

    prompt.value = promptData;
    ratings.value = ratingsData;
    promptStats.value = statsData;
    statistics.value = ratingStatsData;
  } catch (err) {
    console.error('Failed to load prompt details:', err);
    error.value = '상세 정보를 불러오는데 실패했습니다.';
  } finally {
    isLoading.value = false;
  }
};

// Watch for open state
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      loadDetails();
    }
  }
);

// Event handlers
const handleClose = () => {
  emit('update:open', false);
};

const handleRatingSubmitted = async () => {
  // Refresh data after rating submission
  await loadDetails();
  emit('data-updated');
};

const handleSetAsDefault = async () => {
  try {
    await setAsDefaultPrompt(props.promptKey);
    toast.success('기본 프롬프트로 설정되었습니다.');
    await loadDetails();
    emit('data-updated');
  } catch (error) {
    console.error('Failed to set default:', error);
    toast.error('설정 중 오류가 발생했습니다.');
  }
};

const handleDeleteConfirm = async () => {
  try {
    await deletePrompt(props.promptKey);
    toast.success('프롬프트가 삭제되었습니다.');
    emit('update:open', false);
    emit('data-updated');
  } catch (error) {
    console.error('Failed to delete prompt:', error);
    toast.error('삭제 중 오류가 발생했습니다.');
  }
};

const handleDeleteRating = async (ratingKey: number) => {
  if (!confirm('이 평가를 삭제하시겠습니까?')) {
    return;
  }

  try {
    await deleteRating(ratingKey);
    toast.success('평가가 삭제되었습니다.');
    await loadDetails(); // Refresh data
    emit('data-updated');
  } catch (error) {
    console.error('Failed to delete rating:', error);
    toast.error('평가 삭제 중 오류가 발생했습니다.');
  }
};

// Date formatting
const formatDate = (dateStr: string): string => {
  if (!dateStr) return '';

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

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '';

  const date = new Date(dateStr);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};
</script>
