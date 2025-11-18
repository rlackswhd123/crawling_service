<script setup lang="ts">
import { ref, computed } from 'vue';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { processImageWithGemini, removeImageBackground } from '@/services/bangkku/gemini.service';
import defaultFurniture from '@/assets/room-default/default-furniture.jpg';
import PromptEditor from '@/components/bangkku/PromptEditor.vue';
import PromptManagement from '@/components/bangkku/PromptManagement.vue';

const fileInput = ref<HTMLInputElement | null>(null);
const uploadedImage = ref<{ file: File; preview: string } | null>(null);
const isProcessing = ref(false);
const result = ref<string | null>(null);
const error = ref<string | null>(null);
const isDragging = ref(false);
const useDefaultImages = ref(false);
const aiPrompt = ref('');
const isRemovingBackground = ref(false);

// Current images for PromptEditor (single image)
const currentImages = computed(() => {
  return uploadedImage.value ? [uploadedImage.value] : [];
});

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file && file.type.startsWith('image/')) {
    if (uploadedImage.value) {
      URL.revokeObjectURL(uploadedImage.value.preview);
    }
    uploadedImage.value = {
      file,
      preview: URL.createObjectURL(file)
    };
    result.value = null;
    error.value = null;
  }
};

const handleDrop = (event: DragEvent) => {
  isDragging.value = false;
  const file = event.dataTransfer?.files[0];
  if (file && file.type.startsWith('image/')) {
    if (uploadedImage.value) {
      URL.revokeObjectURL(uploadedImage.value.preview);
    }
    uploadedImage.value = {
      file,
      preview: URL.createObjectURL(file)
    };
    result.value = null;
    error.value = null;
  }
};

const handleDragOver = (event: DragEvent) => {
  event.preventDefault();
  isDragging.value = true;
};

const loadDefaultImage = async () => {
  useDefaultImages.value = true;
  result.value = null;
  error.value = null;

  // Convert image URL to File
  const urlToFile = async (url: string, filename: string): Promise<File> => {
    const response = await fetch(url);
    const blob = await response.blob();
    return new File([blob], filename, { type: blob.type });
  };

  try {
    const file = await urlToFile(defaultFurniture, 'default-furniture.jpg');
    uploadedImage.value = {
      file,
      preview: defaultFurniture
    };
  } catch (err) {
    console.error('기본 이미지 로드 실패:', err);
    error.value = '기본 이미지를 불러오는데 실패했습니다.';
  }
};

const processImage = async () => {
  if (!uploadedImage.value) return;

  isProcessing.value = true;
  result.value = null;
  error.value = null;

  try {
    const { editedUrl } = await processImageWithGemini({
      prompt: aiPrompt.value,
      imageFile: uploadedImage.value.file
    });

    result.value = editedUrl;
  } catch (err) {
    console.error('이미지 처리 실패:', err);
    error.value = '처리 중 오류가 발생했습니다.';
  } finally {
    isProcessing.value = false;
  }
};

const downloadResult = () => {
  if (!result.value) return;

  const link = document.createElement('a');
  link.href = result.value;
  const timestamp = new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14);
  link.download = `furniture-front-view-${timestamp}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const regenerate = async () => {
  if (!uploadedImage.value || isProcessing.value) return;
  await processImage();
};

const removeBackground = async () => {
  if (!result.value || isRemovingBackground.value) return;

  isRemovingBackground.value = true;
  error.value = null;

  try {
    const croppedUrl = await removeImageBackground(result.value);
    result.value = croppedUrl;
  } catch (err) {
    console.error('여백 제거 실패:', err);
    error.value = '여백 제거 중 오류가 발생했습니다.';
  } finally {
    isRemovingBackground.value = false;
  }
};

const reset = () => {
  if (uploadedImage.value) {
    URL.revokeObjectURL(uploadedImage.value.preview);
  }
  uploadedImage.value = null;
  result.value = null;
  error.value = null;
  isProcessing.value = false;
  useDefaultImages.value = false;
  // Reset file input to allow re-uploading the same file
  if (fileInput.value) fileInput.value.value = '';
};
</script>

<template>
  <div class="container mx-auto p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🖼️ 가구 드래그 이미지로 변환</h1>
      <p class="text-gray-600">
        다양한 각도의 가구 이미지를 카탈로그용 정면 일러스트로 변환합니다.
      </p>
    </div>

    <!-- Prompt Editor -->
    <PromptEditor
      v-model="aiPrompt"
      prompt-kind="bangkku/furniture-front-view"
      model-kind="gemini-2.5-flash"
      :current-images="currentImages"
    />

    <!-- Default Image Button -->
    <div v-if="!uploadedImage" class="flex gap-4 mb-8">
      <Button @click="loadDefaultImage" variant="outline" class="flex-1">
        🖼️ 기본 이미지 사용
      </Button>
    </div>

    <!-- Upload Area (Conditional) -->
    <div
      v-if="!uploadedImage"
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
        PNG, JPG, WEBP (최대 10MB)
      </p>
    </div>

    <!-- Image Processing Card -->
    <div v-if="uploadedImage" class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Left: Original -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium text-gray-700">원본 이미지</h3>
            <button
              @click="reset"
              class="text-red-500 hover:text-red-700 text-sm"
              :disabled="isProcessing"
            >
              초기화
            </button>
          </div>
          <img
            :src="uploadedImage.preview"
            class="w-full h-96 object-contain rounded-lg border border-gray-200"
            alt="Original"
          />
        </div>

        <!-- Right: Result -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 mb-2">변환 결과</h3>
          <div class="w-full h-96 rounded-lg bg-gray-100 flex items-center justify-center border border-gray-200 overflow-hidden">
            <!-- Processing State -->
            <div v-if="isProcessing" class="text-center">
              <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p class="text-sm text-gray-600">드래그 이미지로 변환 중...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="text-center px-4">
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
              <p class="text-sm text-red-600">{{ error }}</p>
              <Button
                @click="processImage"
                size="sm"
                variant="outline"
                class="mt-2"
              >
                다시 시도
              </Button>
            </div>

            <!-- Success State -->
            <!-- <img
              v-else-if="result"
              :src="result"
              class="w-full h-full object-contain"
              alt="Processed"
            /> -->
            <div
              v-else-if="result"
              class="w-full h-full flex flex-col items-center justify-center gap-4 px-4 py-6"
            >
            <img
                :src="result"
                class="max-h-72 w-full object-contain"
                alt="Processed"
              />
              <div class="flex flex-wrap justify-center gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  @click="downloadResult"
                >
                  이미지 다운로드
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  :disabled="isRemovingBackground"
                  @click="removeBackground"
                >
                  {{ isRemovingBackground ? '여백 제거 중...' : '여백 제거' }}
                </Button>
                <Button
                  size="sm"
                  :disabled="isProcessing"
                  @click="regenerate"
                >
                  다시 생성
                </Button>
              </div>
            </div>


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
                @click="processImage"
                size="sm"
              >
                드래그 이미지로 변환
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Prompt Management -->
    <PromptManagement
      v-model="aiPrompt"
      prompt-kind="bangkku/furniture-front-view"
    />

    <!-- Feature Description -->
    <Card class="mt-8 bg-blue-50 border-blue-200">
      <CardHeader>
        <CardTitle class="text-lg">📖 기능 설명</CardTitle>
      </CardHeader>
      <CardContent class="space-y-2 text-sm text-gray-700">
        <p><strong>이 기능은:</strong> AI를 사용하여 다양한 각도의 가구 이미지를 정면 일러스트 스타일로 변환합니다.</p>
        <p><strong>사용 방법:</strong></p>
        <ul class="list-disc list-inside pl-4 space-y-1">
          <li>변환할 가구 이미지를 업로드하세요 (드래그 앤 드롭 가능)</li>
          <li>필요시 AI 프롬프트를 수정하세요</li>
          <li>"드래그 이미지로 변환" 버튼을 클릭하세요</li>
          <li>원본과 변환된 카탈로그 스타일 이미지를 비교하세요</li>
        </ul>
        <p class="text-xs text-gray-500 mt-2">
          ⚠️ 주의: 이미지 처리에 30-40초 정도 소요됩니다.
        </p>
      </CardContent>
    </Card>
  </div>
</template>
