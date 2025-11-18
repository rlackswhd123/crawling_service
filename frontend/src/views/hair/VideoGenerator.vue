<script setup lang="ts">
import { ref, onUnmounted, computed } from 'vue';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { veo3Service } from '@/services/bangkku/veo3.service';
import { fileToBase64 } from '@/services/common/file.utils';
import defaultConvertHairImg from '@/assets/hair-default/hair-convert-sample.png';
import PromptEditor from '@/components/bangkku/PromptEditor.vue';
import PromptManagement from '@/components/bangkku/PromptManagement.vue';

const fileInput = ref<HTMLInputElement | null>(null);
const uploadedImage = ref<{ file: File; preview: string } | null>(null);
const isDragging = ref(false);
const useDefaultImages = ref(false);
const prompt = ref(`
세계 최고 수준의 영상 합성 감독으로서, 업로드된 이미지를 기반으로 다음 장면을 만드세요.

장면 설정:
- 인물이 바람이 부는 거리나 자연 속을 걸어가고 있습니다.
- 인물의 머릿결이 자연스럽게 바람에 휘날리며 움직입니다.
- 조명은 부드럽고, 피부 톤과 배경의 색감은 현실적으로 유지됩니다.
- 인물의 시선, 자세, 옷의 움직임이 자연스럽게 표현되며, 
  원본 이미지의 얼굴 특징은 유지하지만 표정이 미세하게 생동감 있게 변해야 합니다.

연출 지침:
- 인물은 정면 또는 측면으로 걷고 있으며, 카메라는 천천히 인물을 따라가거나 회전하며 움직입니다.
- 머리카락은 실제처럼 움직이고, 배경에 바람의 흔적이 느껴지게 하세요.
- 전체 영상은 현실적인 질감과 영화 같은 분위기를 유지해야 합니다.
- 추가적인 텍스트, 자막, 워터마크, 그래픽 요소는 포함하지 마세요.
- 원본 이미지를 그대로 정지 화면으로 보여주지 말고, 움직임과 바람의 흐름이 있는 새로운 영상을 생성하세요.

출력 조건:
- 5~10초 길이의 영상으로 생성하세요.
- 카메라 모션은 부드럽고, 인물의 중심이 벗어나지 않게 유지하세요.
`);

const isGenerating = ref(false);
const progress = ref(0);
const statusMessage = ref('');
const videoResult = ref<string | null>(null);

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
  }
};

const handleDragOver = (event: DragEvent) => {
  event.preventDefault();
  isDragging.value = true;
};

const loadDefaultImage = async () => {
  useDefaultImages.value = true;

  const urlToFile = async (url: string, filename: string): Promise<File> => {
    const response = await fetch(url);
    const blob = await response.blob();
    return new File([blob], filename, { type: blob.type });
  };

  try {
    const defaultFile = await urlToFile(defaultConvertHairImg, 'hair-convert-sample.png');

    if (uploadedImage.value) {
      URL.revokeObjectURL(uploadedImage.value.preview);
    }

    uploadedImage.value = {
      file: defaultFile,
      preview: defaultConvertHairImg
    };
  } catch (err) {
    console.error('기본 이미지 로드 실패:', err);
    alert('기본 이미지를 불러오는데 실패했습니다.');
  }
};

const clearImage = () => {
  if (uploadedImage.value) {
    URL.revokeObjectURL(uploadedImage.value.preview);
  }
  uploadedImage.value = null;
  useDefaultImages.value = false;
  videoResult.value = null;
  if (fileInput.value) fileInput.value.value = '';
};

const generateVideo = async () => {
  if (!uploadedImage.value || !prompt.value.trim()) {
    alert('이미지와 프롬프트를 입력해주세요.');
    return;
  }

  isGenerating.value = true;
  videoResult.value = null;
  progress.value = 0;
  statusMessage.value = '준비 중...';

  try {
    // File → Base64 변환
    const imageBase64 = await fileToBase64(uploadedImage.value.file);

    // WebSocket으로 비디오 생성
    await veo3Service.generateVideo(
      {
        prompt: prompt.value,
        image: imageBase64
      },
      {
        onProgress: (percent: number, message: string) => {
          progress.value = percent;
          statusMessage.value = message;
        },
        onCompleted: (result) => {
          videoResult.value = result.video_url;
          isGenerating.value = false;
          statusMessage.value = '완료!';
        },
        onError: (error: string) => {
          alert(`비디오 생성 실패: ${error}`);
          isGenerating.value = false;
          progress.value = 0;
          statusMessage.value = '';
        }
      }
    );
  } catch (error) {
    console.error('Video generation error:', error);
    alert(`오류 발생: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    isGenerating.value = false;
    progress.value = 0;
    statusMessage.value = '';
  }
};

const downloadVideo = () => {
  if (!videoResult.value) return;

  // Create download link
  const link = document.createElement('a');
  link.href = videoResult.value;
  link.download = `generated-video-${Date.now()}.mp4`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// WebSocket cleanup
onUnmounted(() => {
  veo3Service.closeConnection();
});
</script>

<template>
  <div class="container mx-auto p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🎬 비디오 생성</h1>
      <p class="text-gray-600">
        정적 이미지를 동적 비디오로 변환합니다. (Veo 3.1)
      </p>
    </div>

    <!-- Prompt Editor -->
    <PromptEditor
      v-model="prompt"
      prompt-kind="bangkku/video-generation"
      model-kind="veo-3.1"
      :current-images="currentImages"
    />

    <div class="grid grid-cols-2 gap-8">
      <!-- Left: Upload & Settings -->
      <div class="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>이미지 업로드</CardTitle>
            <CardDescription>
              비디오로 변환할 이미지를 업로드하세요.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div
              class="border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors"
              :class="isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'"
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

              <div v-if="!uploadedImage">
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
                <p class="text-lg text-gray-600 mb-2">클릭하거나 이미지를 드래그하세요</p>
                <p class="text-sm text-gray-400">PNG, JPG, WEBP (최대 10MB)</p>
              </div>

              <div v-else>
                <img
                  :src="uploadedImage.preview"
                  class="w-full rounded-lg"
                  alt="Source image"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Default Image / Clear Buttons -->
        <div class="flex gap-4 mb-6">
          <Button
            v-if="!uploadedImage"
            @click="loadDefaultImage"
            variant="outline"
            class="flex-1"
          >
            🖼️ 기본 이미지 사용
          </Button>
          <Button
            v-else
            @click="clearImage"
            variant="outline"
            class="flex-1"
          >
            이미지 초기화
          </Button>
        </div>

        <Button
          @click="generateVideo"
          :disabled="!uploadedImage || !prompt || isGenerating"
          class="w-full"
          size="lg"
        >
          {{ isGenerating ? '비디오 생성 중...' : '비디오 생성 시작' }}
        </Button>
      </div>

      <!-- Right: Progress & Result -->
      <div class="space-y-6">
        <!-- Progress Card -->
        <Card v-if="isGenerating">
          <CardHeader>
            <CardTitle>생성 진행 중</CardTitle>
            <CardDescription>
              비디오 생성에는 2-10분이 소요됩니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div class="flex justify-between text-sm">
                <span>{{ statusMessage }}</span>
                <span>{{ progress }}%</span>
              </div>

              <div class="w-full bg-gray-200 rounded-full h-3">
                <div
                  class="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  :style="{ width: `${progress}%` }"
                />
              </div>

              <div class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Result Card -->
        <Card v-if="videoResult">
          <CardHeader>
            <CardTitle>생성 완료</CardTitle>
            <CardDescription>
              비디오가 성공적으로 생성되었습니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div class="rounded-lg overflow-hidden">
              <video
                v-if="videoResult"
                :src="videoResult"
                controls
                autoplay
                loop
                class="w-full rounded-lg"
              >
                Your browser does not support the video tag.
              </video>
            </div>

            <div class="flex gap-4 mt-4">
              <Button
                variant="outline"
                class="flex-1"
                @click="downloadVideo"
                :disabled="!videoResult"
              >
                다운로드
              </Button>
              <Button variant="outline" class="flex-1">
                다시 생성
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Prompt Management -->
    <PromptManagement
      v-model="prompt"
      prompt-kind="bangkku/video-generation"
    />

    <!-- Feature Description -->
    <Card class="mt-8 bg-blue-50 border-blue-200">
      <CardHeader>
        <CardTitle class="text-lg">📖 기능 설명</CardTitle>
      </CardHeader>
      <CardContent class="space-y-2 text-sm text-gray-700">
        <p><strong>이 기능은:</strong> Google Veo 3.1을 사용하여 정적 이미지에 카메라 모션을 추가해 동적 비디오를 생성합니다.</p>
        <p><strong>사용 방법:</strong></p>
        <ul class="list-disc list-inside pl-4 space-y-1">
          <li>변환할 이미지를 업로드하세요 (드래그 앤 드롭 가능)</li>
          <li>AI가 자동으로 카메라 모션 프롬프트를 생성하거나 직접 작성하세요</li>
          <li>"비디오 생성 시작" 버튼을 클릭하세요</li>
          <li>생성 진행 상황을 확인하세요</li>
        </ul>
        <p class="text-xs text-gray-500 mt-2">
          ⚠️ 주의: 비디오 생성에 2-10분 정도 소요됩니다. (현재 시뮬레이션 모드)
        </p>
      </CardContent>
    </Card>
  </div>
</template>
