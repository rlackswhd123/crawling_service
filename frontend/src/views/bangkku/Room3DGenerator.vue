<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { processMultipleImagesWithGemini } from '@/services/bangkku/gemini.service';
import type { RoomStructure } from '@/types/room3d.types';
import { ROOM_STRUCTURE_CONFIGS } from '@/types/room3d.types';
import PromptEditor from '@/components/bangkku/PromptEditor.vue';
import PromptManagement from '@/components/bangkku/PromptManagement.vue';

// Import default images
import leftWallDefault from '@/assets/room-default/left-wall.png';
import frontWallDefault from '@/assets/room-default/front-wall.png';
import rightWallDefault from '@/assets/room-default/right-wall.png';
import emptyRoomDefault from '@/assets/room-default/empty-room.png';

type ImageKey = 'left' | 'front' | 'right' | 'background';

interface ImageData {
  file: File;
  preview: string;
}

// Room structure selection
const roomStructure = ref<RoomStructure>('ㄷ자');

const leftInput = ref<HTMLInputElement | null>(null);
const frontInput = ref<HTMLInputElement | null>(null);
const rightInput = ref<HTMLInputElement | null>(null);
const backgroundInput = ref<HTMLInputElement | null>(null);

const images = ref<Record<ImageKey, ImageData | null>>({
  left: null,
  front: null,
  right: null,
  background: null
});

const isProcessing = ref(false);
const result = ref<string | null>(null);
const error = ref<string | null>(null);
const useDefaultImages = ref(false);

// Current images for PromptEditor
const currentImages = computed(() => {
  const imageArray = [];
  if (images.value.left) imageArray.push(images.value.left);
  if (images.value.front) imageArray.push(images.value.front);
  if (images.value.right) imageArray.push(images.value.right);
  if (images.value.background) imageArray.push(images.value.background);
  return imageArray;
});

// Get current structure config
const currentStructureConfig = computed(() => {
  return ROOM_STRUCTURE_CONFIGS.find(c => c.name === roomStructure.value)!;
});

// Dynamic prompt kind based on room structure
const promptKind = computed(() => {
  const shapeMap: Record<RoomStructure, string> = {
    'ㅡ자': 'ㅡ-shape',
    'ㄱ자': 'ㄱ-shape',
    'ㄷ자': 'ㄷ-shape'
  };
  return `bangkku/3d-room-generator/${shapeMap[roomStructure.value]}`;
});

// AI prompt - will be loaded from DB by PromptEditor
const aiPrompt = ref('');

// Track if user has manually edited the prompt
const hasManualEdits = ref(false);
const initialPromptLoaded = ref(false);

// Watch for prompt changes to track manual edits
watch(aiPrompt, (newValue, oldValue) => {
  if (initialPromptLoaded.value && newValue !== oldValue) {
    hasManualEdits.value = true;
  }
});

// Watch for initial prompt load from PromptEditor
watch(aiPrompt, (newValue) => {
  if (newValue && !initialPromptLoaded.value) {
    initialPromptLoaded.value = true;
  }
});

// Structure change confirmation dialog
const showConfirmDialog = ref(false);
const pendingStructureChange = ref<RoomStructure | null>(null);

// Handle structure change with confirmation
const handleStructureChange = (newStructure: RoomStructure) => {
  if (hasManualEdits.value && newStructure !== roomStructure.value) {
    pendingStructureChange.value = newStructure;
    showConfirmDialog.value = true;
  } else {
    roomStructure.value = newStructure;
    hasManualEdits.value = false;
  }
};

// Confirm structure change and reset prompt
const confirmStructureChange = () => {
  if (pendingStructureChange.value) {
    roomStructure.value = pendingStructureChange.value;
    hasManualEdits.value = false;
    initialPromptLoaded.value = false;
    aiPrompt.value = ''; // Will trigger PromptEditor to reload
    showConfirmDialog.value = false;
    pendingStructureChange.value = null;
  }
};

// Cancel structure change
const cancelStructureChange = () => {
  showConfirmDialog.value = false;
  pendingStructureChange.value = null;
};

// Legacy hardcoded prompt (replaced by computed aiPrompt)
const legacyPrompt = ref(`Create a realistic 3D room visualization showing a ㄷ-shaped (U-shaped) closet/dressing room layout.

IMAGE INPUTS (4 images):
1. Left wall furniture layout
2. Front wall furniture layout (3 units)
3. Right wall furniture layout
4. Empty room reference (lighting, walls, floor)

SPATIAL SPECIFICATIONS:
Left Wall:
- Position: Left side of the room
- Furniture from Image 1: Maintain exact structure and proportions
- Width: Approximately 800mm per unit
- Floor-to-ceiling height

Front Wall (Center):
- Position: Back wall of the room
- Furniture from Image 2: Three connected units
- Total width: Approximately 2400mm (800mm × 3)
- Central focus of the room
- Floor-to-ceiling height

Right Wall:
- Position: Right side of the room
- Furniture from Image 3: Mirror the left wall layout
- Width: Approximately 800mm per unit
- Floor-to-ceiling height

ROOM ATMOSPHERE:
- Use Image 4 as reference for:
  * Lighting conditions and quality
  * Wall color and texture
  * Floor material and pattern
  * Overall room ambiance

PERSPECTIVE & COMPOSITION:
- 3D perspective from room entrance
- Viewer standing at the open side of the ㄷ-shape
- Can see all three walls clearly
- Natural depth and spatial relationships
- Realistic vanishing point

IMPORTANT REQUIREMENTS:
- Maintain EXACT furniture structure from reference images
- Preserve all design details and proportions
- Connect furniture units seamlessly at corners
- Remove all UI elements, labels, and annotations
- Professional interior design visualization quality
- Photorealistic rendering

OUTPUT:
A complete 3D room visualization showing the ㄷ-shaped layout with all three furniture walls integrated into a cohesive space. The result should look like a professional interior design rendering suitable for client presentations.`);

// Check if all required images are uploaded based on structure
const allImagesUploaded = computed(() => {
  if (useDefaultImages.value) return true;

  const config = currentStructureConfig.value;
  const requiredWalls = config.walls;

  // Background is always required
  if (!images.value.background) return false;

  // Check each required wall
  for (const wall of requiredWalls) {
    if (!images.value[wall]) return false;
  }

  return true;
});

const triggerFileInput = (key: ImageKey) => {
  const inputs = {
    left: leftInput,
    front: frontInput,
    right: rightInput,
    background: backgroundInput
  };
  inputs[key].value?.click();
};

const handleFileSelect = (event: Event, key: ImageKey) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file && file.type.startsWith('image/')) {
    if (images.value[key]) {
      URL.revokeObjectURL(images.value[key]!.preview);
    }
    images.value[key] = {
      file,
      preview: URL.createObjectURL(file)
    };
  }
};

const loadDefaultImages = async () => {
  useDefaultImages.value = true;
  result.value = null;
  error.value = null;

  // Convert image URLs to Files
  const urlToFile = async (url: string, filename: string): Promise<File> => {
    const response = await fetch(url);
    const blob = await response.blob();
    return new File([blob], filename, { type: blob.type });
  };

  try {
    const config = currentStructureConfig.value;
    const requiredWalls = config.walls;

    // Always load background
    const bgFile = await urlToFile(emptyRoomDefault, 'empty-room.png');

    // Load only required wall images
    const wallPromises: Promise<File>[] = [];
    const wallKeys: ('left' | 'front' | 'right')[] = [];

    if (requiredWalls.includes('left')) {
      wallPromises.push(urlToFile(leftWallDefault, 'left-wall.png'));
      wallKeys.push('left');
    }
    if (requiredWalls.includes('front')) {
      wallPromises.push(urlToFile(frontWallDefault, 'front-wall.png'));
      wallKeys.push('front');
    }
    if (requiredWalls.includes('right')) {
      wallPromises.push(urlToFile(rightWallDefault, 'right-wall.png'));
      wallKeys.push('right');
    }

    const wallFiles = await Promise.all(wallPromises);

    // Reset all images
    images.value = {
      left: null,
      front: null,
      right: null,
      background: { file: bgFile, preview: emptyRoomDefault }
    };

    // Set only required wall images
    wallKeys.forEach((key, index) => {
      const defaultUrls = {
        left: leftWallDefault,
        front: frontWallDefault,
        right: rightWallDefault
      };
      images.value[key] = {
        file: wallFiles[index],
        preview: defaultUrls[key]
      };
    });
  } catch (err) {
    console.error('기본 이미지 로드 실패:', err);
    error.value = '기본 이미지를 불러오는데 실패했습니다.';
  }
};

const clearImages = () => {
  images.value = {
    left: null,
    front: null,
    right: null,
    background: null
  };
  result.value = null;
  error.value = null;
  useDefaultImages.value = false;
  // Reset all file inputs to allow re-uploading the same files
  if (leftInput.value) leftInput.value.value = '';
  if (frontInput.value) frontInput.value.value = '';
  if (rightInput.value) rightInput.value.value = '';
  if (backgroundInput.value) backgroundInput.value.value = '';
};

const generate3DRoom = async () => {
  if (!allImagesUploaded.value) return;

  isProcessing.value = true;
  result.value = null;
  error.value = null;

  try {
    const config = currentStructureConfig.value;
    const requiredWalls = config.walls;

    // Prepare images in order based on structure
    const imageFiles: File[] = [];

    // Add wall images in order: left, front, right (if required)
    if (requiredWalls.includes('left') && images.value.left) {
      imageFiles.push(images.value.left.file);
    }
    if (requiredWalls.includes('front') && images.value.front) {
      imageFiles.push(images.value.front.file);
    }
    if (requiredWalls.includes('right') && images.value.right) {
      imageFiles.push(images.value.right.file);
    }

    // Always add background last
    imageFiles.push(images.value.background!.file);

    const { editedUrl } = await processMultipleImagesWithGemini({
      prompt: aiPrompt.value,
      imageFiles
    });

    result.value = editedUrl;
  } catch (err) {
    console.error('3D 룸 생성 실패:', err);
    error.value = '3D 룸 생성 중 오류가 발생했습니다.';
  } finally {
    isProcessing.value = false;
  }
};
</script>

<template>
  <div class="container mx-auto p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🏠 3D 룸 생성</h1>
      <p class="text-gray-600">
        2D 가구 배치도를 3D 공간으로 변환합니다.
      </p>
    </div>

    <!-- Structure Selection -->
    <Card class="mb-8">
      <CardHeader>
        <CardTitle>방 구조 선택</CardTitle>
        <CardDescription>
          생성하고자 하는 방의 구조를 선택하세요.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div class="flex items-center gap-4">
          <label class="text-sm font-medium text-gray-700 w-24">
            구조:
          </label>
          <Select :model-value="roomStructure" @update:model-value="handleStructureChange">
            <SelectTrigger class="w-[280px]">
              <SelectValue placeholder="구조 선택" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem
                v-for="config in ROOM_STRUCTURE_CONFIGS"
                :key="config.name"
                :value="config.name"
              >
                {{ config.label }}
              </SelectItem>
            </SelectContent>
          </Select>
          <div class="flex-1 text-sm text-gray-600">
            {{ currentStructureConfig.description }}
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Prompt Editor (Editable Mode - Loaded from DB) -->
    <PromptEditor
      v-model="aiPrompt"
      :prompt-kind="promptKind"
      model-kind="gemini-2.5-flash"
      :current-images="currentImages"
      :readonly="false"
      class="mb-8"
    />

    <!-- Quick Actions -->
    <div v-if="!allImagesUploaded" class="flex gap-4 mb-8">
      <Button @click="loadDefaultImages" variant="outline" class="flex-1">
        🖼️ 기본 이미지 사용
      </Button>
    </div>

    <div v-if="allImagesUploaded && !result" class="flex gap-4 mb-8">
      <Button @click="clearImages" variant="outline">
        🔄 이미지 초기화
      </Button>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>{{ currentStructureConfig.wallCount + 1 }}개 이미지 업로드</CardTitle>
        <CardDescription>
          {{ currentStructureConfig.label }}에 필요한 벽면 이미지와 배경 이미지를 업로드하세요.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-2 gap-4">
          <!-- Left Wall - Conditional -->
          <div v-if="currentStructureConfig.walls.includes('left')">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              좌측 벽
            </label>
            <div
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500"
              @click="() => triggerFileInput('left')"
            >
              <input
                ref="leftInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="(e) => handleFileSelect(e, 'left')"
              />
              <div v-if="!images.left">
                <div class="text-3xl mb-2">⬅️</div>
                <p class="text-sm text-gray-500">좌측 벽 이미지</p>
              </div>
              <img v-else :src="images.left.preview" class="w-full rounded" alt="Left wall" />
            </div>
          </div>

          <!-- Front Wall - Conditional -->
          <div v-if="currentStructureConfig.walls.includes('front')">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              정면 벽
            </label>
            <div
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500"
              @click="() => triggerFileInput('front')"
            >
              <input
                ref="frontInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="(e) => handleFileSelect(e, 'front')"
              />
              <div v-if="!images.front">
                <div class="text-3xl mb-2">⬆️</div>
                <p class="text-sm text-gray-500">정면 벽 이미지 (3 units)</p>
              </div>
              <img v-else :src="images.front.preview" class="w-full rounded" alt="Front wall" />
            </div>
          </div>

          <!-- Right Wall - Conditional -->
          <div v-if="currentStructureConfig.walls.includes('right')">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              우측 벽
            </label>
            <div
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500"
              @click="() => triggerFileInput('right')"
            >
              <input
                ref="rightInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="(e) => handleFileSelect(e, 'right')"
              />
              <div v-if="!images.right">
                <div class="text-3xl mb-2">➡️</div>
                <p class="text-sm text-gray-500">우측 벽 이미지</p>
              </div>
              <img v-else :src="images.right.preview" class="w-full rounded" alt="Right wall" />
            </div>
          </div>

          <!-- Background -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              배경 (빈 방)
            </label>
            <div
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500"
              @click="() => triggerFileInput('background')"
            >
              <input
                ref="backgroundInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="(e) => handleFileSelect(e, 'background')"
              />
              <div v-if="!images.background">
                <div class="text-3xl mb-2">🏠</div>
                <p class="text-sm text-gray-500">빈 방 배경</p>
              </div>
              <img v-else :src="images.background.preview" class="w-full rounded" alt="Background" />
            </div>
          </div>
        </div>

        <Button
          @click="generate3DRoom"
          :disabled="!allImagesUploaded || isProcessing"
          class="w-full mt-4"
        >
          {{ isProcessing ? '생성 중...' : '3D 룸 생성' }}
        </Button>
      </CardContent>
    </Card>

    <!-- Processing/Result Section -->
    <div v-if="allImagesUploaded" class="mt-8 bg-white rounded-lg border border-gray-200 p-4">
      <h3 class="text-lg font-medium text-gray-700 mb-4">3D 룸 생성 결과</h3>

      <div class="w-full rounded-lg bg-gray-100 flex items-center justify-center border border-gray-200 overflow-hidden" style="min-height: 600px;">
        <!-- Processing State -->
        <div v-if="isProcessing" class="text-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">3D 룸 생성 중...</p>
          <p class="text-sm text-gray-500 mt-2">5-10초 정도 소요됩니다</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center px-4">
          <svg
            class="w-16 h-16 text-red-500 mx-auto mb-4"
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
          <p class="text-red-600 mb-4">{{ error }}</p>
          <Button @click="generate3DRoom" size="sm" variant="outline">
            다시 시도
          </Button>
        </div>

        <!-- Success State -->
        <img
          v-else-if="result"
          :src="result"
          class="w-full h-full object-contain"
          alt="3D room result"
        />

        <!-- Empty State -->
        <div v-else class="text-center px-4">
          <svg
            class="w-16 h-16 text-gray-400 mx-auto mb-4"
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
          <p class="text-gray-500 mb-4">위 버튼을 눌러 3D 룸을 생성하세요</p>
        </div>
      </div>
    </div>

    <!-- Prompt Management -->
    <PromptManagement
      v-model="aiPrompt"
      :prompt-kind="promptKind"
    />

    <!-- Structure Change Confirmation Dialog -->
    <AlertDialog :open="showConfirmDialog" @update:open="showConfirmDialog = $event">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>방 구조를 변경하시겠습니까?</AlertDialogTitle>
          <AlertDialogDescription>
            AI 프롬프트를 수정하셨습니다. 방 구조를 변경하면 현재 편집한 프롬프트가 초기화되고
            새로운 구조에 맞는 기본 프롬프트가 로드됩니다.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel @click="cancelStructureChange">
            취소
          </AlertDialogCancel>
          <AlertDialogAction @click="confirmStructureChange">
            변경
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>

    <!-- Feature Description -->
    <Card class="mt-8 bg-blue-50 border-blue-200">
      <CardHeader>
        <CardTitle class="text-lg">📖 기능 설명</CardTitle>
      </CardHeader>
      <CardContent class="space-y-2 text-sm text-gray-700">
        <p><strong>이 기능은:</strong> AI를 사용하여 {{ currentStructureConfig.wallCount }}개의 2D 가구 배치도를 {{ currentStructureConfig.name }} 3D 공간으로 변환합니다.</p>
        <p><strong>필요한 이미지:</strong></p>
        <ul class="list-disc list-inside pl-4 space-y-1">
          <li v-if="currentStructureConfig.walls.includes('left')"><strong>좌측 벽:</strong> 왼쪽 벽면 가구 배치도</li>
          <li v-if="currentStructureConfig.walls.includes('front')"><strong>정면 벽:</strong> 뒷면 중앙 벽 가구 배치도</li>
          <li v-if="currentStructureConfig.walls.includes('right')"><strong>우측 벽:</strong> 오른쪽 벽면 가구 배치도</li>
          <li><strong>배경:</strong> 빈 방 참조 이미지 (조명, 벽, 바닥)</li>
        </ul>
        <p><strong>사용 방법:</strong></p>
        <ul class="list-disc list-inside pl-4 space-y-1">
          <li>원하는 방 구조({{ currentStructureConfig.label }})를 선택하세요</li>
          <li>{{ currentStructureConfig.wallCount + 1 }}개 이미지를 모두 업로드하거나 "기본 이미지 사용" 버튼으로 테스트하세요</li>
          <li>필요시 AI 프롬프트를 확인하세요 (자동 생성됨)</li>
          <li>"3D 룸 생성" 버튼을 클릭하세요</li>
        </ul>
        <p class="text-xs text-gray-500 mt-2">
          ℹ️ 주의: 이미지 처리에 30-40초 정도 소요됩니다.
        </p>
      </CardContent>
    </Card>
  </div>
</template>
