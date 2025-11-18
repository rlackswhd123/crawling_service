<script setup lang="ts">
import { ref, computed } from 'vue';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { processImageWithGemini } from '@/services/bangkku/gemini.service';
import defaultFurnitureRoom from '@/assets/room-default/default-furniture-room.png';
import PromptEditor from '@/components/bangkku/PromptEditor.vue';
import PromptManagement from '@/components/bangkku/PromptManagement.vue';

interface ProcessedImage {
  id: string;
  originalFile: File;
  originalUrl: string;
  result: string | null;
  isProcessing: boolean;
  error: string | null;
}

const fileInput = ref<HTMLInputElement | null>(null);
const images = ref<ProcessedImage[]>([]);
const isDragging = ref(false);
const aiPrompt = ref('');
const canAddMore = ref(true);
const useDefaultImages = ref(false);

// Current images for PromptEditor
const currentImages = computed(() => {
  return images.value.map(img => ({
    originalFile: img.originalFile,
    originalUrl: img.originalUrl
  }));
});

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = Array.from(target.files || []);
  addFiles(files);
};

const handleDrop = (event: DragEvent) => {
  isDragging.value = false;
  const files = Array.from(event.dataTransfer?.files || []);
  addFiles(files);
};

const handleDragOver = (event: DragEvent) => {
  event.preventDefault();
  isDragging.value = true;
};

const addFiles = (files: File[]) => {
  const imageFiles = files.filter(file => file.type.startsWith('image/'));
  const availableSlots = 10 - images.value.length;
  const newFiles = imageFiles.slice(0, availableSlots);

  newFiles.forEach(file => {
    const id = `${Date.now()}-${Math.random()}`;
    images.value.push({
      id,
      originalFile: file,
      originalUrl: URL.createObjectURL(file),
      result: null,
      isProcessing: false,
      error: null
    });
  });

  canAddMore.value = images.value.length < 10;
};

const loadDefaultImages = async () => {
  useDefaultImages.value = true;

  const urlToFile = async (url: string, filename: string): Promise<File> => {
    const response = await fetch(url);
    const blob = await response.blob();
    return new File([blob], filename, { type: blob.type });
  };

  try {
    const furnitureFile = await urlToFile(defaultFurnitureRoom, 'default-furniture-room.png');

    images.value = [
      {
        id: `${Date.now()}-1`,
        originalFile: furnitureFile,
        originalUrl: defaultFurnitureRoom,
        result: null,
        isProcessing: false,
        error: null
      }
    ];

    canAddMore.value = images.value.length < 10;
  } catch (err) {
    console.error('기본 이미지 로드 실패:', err);
    alert('기본 이미지를 불러오는데 실패했습니다.');
  }
};

const removeImage = (id: string) => {
  const index = images.value.findIndex(img => img.id === id);
  if (index !== -1) {
    URL.revokeObjectURL(images.value[index].originalUrl);
    if (images.value[index].result && images.value[index].result !== 'error') {
      // Result URLs are data URLs, no need to revoke
    }
    images.value.splice(index, 1);
    canAddMore.value = images.value.length < 10;
    // Reset file input to allow re-uploading the same file
    if (fileInput.value) fileInput.value.value = '';
  }
};

const processImage = async (imageId: string) => {
  const image = images.value.find(img => img.id === imageId);
  if (!image || image.isProcessing) return;

  image.isProcessing = true;
  image.error = null;
  image.result = null;

  try {
    const { editedUrl } = await processImageWithGemini({
      prompt: aiPrompt.value,
      imageFile: image.originalFile
    });

    image.result = editedUrl;
  } catch (error) {
    console.error('이미지 처리 실패:', error);
    image.error = '처리 중 오류가 발생했습니다.';
  } finally {
    image.isProcessing = false;
  }
};

const processAllImages = async () => {
  for (const image of images.value) {
    if (!image.result && !image.isProcessing) {
      await processImage(image.id);
    }
  }
};

const clearAll = () => {
  images.value.forEach(img => {
    URL.revokeObjectURL(img.originalUrl);
  });
  images.value = [];
  canAddMore.value = true;
  useDefaultImages.value = false;
  // Reset file input to allow re-uploading the same file
  if (fileInput.value) fileInput.value.value = '';
};
</script>

<template>
  <div class="container mx-auto p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🛋️ 가구 제거</h1>
      <p class="text-gray-600">
        방 사진에서 가구를 자동으로 제거하여 빈 공간을 시각화합니다.
      </p>
    </div>

    <!-- Prompt Editor -->
    <PromptEditor
      v-model="aiPrompt"
      prompt-kind="bangkku/furniture-removal"
      model-kind="gemini-2.5-flash"
      :current-images="currentImages"
    />

    <!-- Default Images Button -->
    <div v-if="!images.length" class="flex gap-4 mb-8">
      <Button @click="loadDefaultImages" variant="outline" class="flex-1">
        🖼️ 기본 이미지 사용
      </Button>
    </div>

    <!-- Upload Area (Conditional) -->
    <div
      v-if="canAddMore"
      class="mb-8 border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer"
      :class="isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white hover:border-blue-400'"
      @click="triggerFileInput"
      @dragover.prevent="handleDragOver"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        multiple
        class="hidden"
        @change="handleFileSelect"
      />

      <svg
        class="w-12 h-12 mx-auto mb-4 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>

      <p class="text-lg text-gray-600 mb-2">
        클릭하거나 이미지를 드래그하세요
      </p>
      <p class="text-sm text-gray-400">
        PNG, JPG, WEBP (최대 10MB) • {{ images.length }}/10 업로드됨
      </p>
    </div>

    <!-- Action Buttons -->
    <div v-if="images.length" class="flex gap-4 mb-8">
      <Button
        @click="processAllImages"
        :disabled="images.some(img => img.isProcessing)"
        class="flex-1"
      >
        {{ images.some(img => img.isProcessing) ? '처리 중...' : '모두 처리' }}
      </Button>
      <Button
        variant="outline"
        @click="clearAll"
        :disabled="images.some(img => img.isProcessing)"
      >
        전체 초기화
      </Button>
    </div>

    <!-- Images Grid -->
    <div v-if="images.length" class="space-y-6">
      <div
        v-for="image in images"
        :key="image.id"
        class="bg-white rounded-lg border border-gray-200 p-4"
      >
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Left: Original -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-gray-700">원본 이미지</h3>
              <button
                @click="removeImage(image.id)"
                class="text-red-500 hover:text-red-700 text-sm"
                :disabled="image.isProcessing"
              >
                삭제
              </button>
            </div>
            <img
              :src="image.originalUrl"
              class="w-full h-96 object-contain rounded-lg border border-gray-200"
              alt="Original"
            />
          </div>

          <!-- Right: Result -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-2">처리 결과</h3>
            <div class="w-full h-96 rounded-lg bg-gray-100 flex items-center justify-center border border-gray-200 overflow-hidden">
              <!-- Processing State -->
              <div v-if="image.isProcessing" class="text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p class="text-sm text-gray-600">가구 제거 중...</p>
              </div>

              <!-- Error State -->
              <div v-else-if="image.error" class="text-center px-4">
                <svg
                  class="w-12 h-12 text-red-500 mx-auto mb-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p class="text-sm text-red-600">{{ image.error }}</p>
                <Button
                  @click="processImage(image.id)"
                  size="sm"
                  variant="outline"
                  class="mt-2"
                >
                  다시 시도
                </Button>
              </div>

              <!-- Success State -->
              <img
                v-else-if="image.result"
                :src="image.result"
                class="w-full h-full object-contain"
                alt="Processed"
              />

              <!-- Empty State -->
              <div v-else class="text-center px-4">
                <svg
                  class="w-12 h-12 text-gray-400 mx-auto mb-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <p class="text-sm text-gray-500 mb-2">처리 대기 중</p>
                <Button
                  @click="processImage(image.id)"
                  size="sm"
                >
                  가구 제거
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Prompt Management -->
    <PromptManagement
      v-model="aiPrompt"
      prompt-kind="bangkku/furniture-removal"
    />

    <!-- Feature Description -->
    <Card class="mt-8 bg-blue-50 border-blue-200">
      <CardHeader>
        <CardTitle class="text-lg">📖 기능 설명</CardTitle>
      </CardHeader>
      <CardContent class="space-y-2 text-sm text-gray-700">
        <p><strong>이 기능은:</strong> AI를 사용하여 방 사진에서 가구, 소품, 장식물을 자동으로 제거합니다.</p>
        <p><strong>사용 방법:</strong></p>
        <ul class="list-disc list-inside pl-4 space-y-1">
          <li>최대 10개의 방 이미지를 업로드하세요 (드래그 앤 드롭 가능)</li>
          <li>필요시 AI 프롬프트를 수정하세요</li>
          <li>각 이미지별로 "가구 제거" 버튼을 클릭하거나 "모두 처리" 버튼으로 일괄 처리하세요</li>
          <li>원본과 결과를 비교하여 확인하세요</li>
        </ul>
        <p class="text-xs text-gray-500 mt-2">
          ⚠️ 주의: 각 이미지 처리에 30-40초 정도 소요됩니다.
        </p>
      </CardContent>
    </Card>
  </div>
</template>
