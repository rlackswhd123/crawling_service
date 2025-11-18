<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { createPromptWithImages, getDefaultPrompt } from '@/services/common/prompt.service';

interface Props {
  modelValue: string;
  promptKind: string;
  modelKind?: string;
  currentImages?: { file: File; preview: string }[] | { originalFile: File; originalUrl: string }[];
  readonly?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  currentImages: () => [],
  readonly: false
});

const emit = defineEmits<{
  'update:modelValue': [value: string];
  'promptSaved': [];
}>();

const isOpen = ref(false);
const isSaving = ref(false);
const saveMessage = ref('');

// Computed property to handle different image structure formats
const imagePreviewUrls = computed(() => {
  return props.currentImages.map(img => {
    // FurnitureRemoval/Room3D format: { originalFile, originalUrl }
    if ('originalUrl' in img) {
      return img.originalUrl;
    }
    // FurnitureFrontView/VideoGenerator format: { file, preview }
    if ('preview' in img) {
      return img.preview;
    }
    return '';
  });
});

// Get File objects from current images
const getImageFiles = (): File[] => {
  return props.currentImages.map(img => {
    if ('originalFile' in img) {
      return img.originalFile;
    }
    if ('file' in img) {
      return img.file;
    }
    return null;
  }).filter((file): file is File => file !== null);
};

const handleSavePrompt = async () => {
  if (isSaving.value) return;

  isSaving.value = true;
  saveMessage.value = '';

  try {
    const imageFiles = getImageFiles();

    await createPromptWithImages({
      promptKind: props.promptKind,
      promptText: props.modelValue,
      isDefaultYn: 0,
      modelKind: props.modelKind,
      imageFiles
    });

    saveMessage.value = '✅ 프롬프트가 저장되었습니다!';
    emit('promptSaved');

    setTimeout(() => {
      saveMessage.value = '';
    }, 3000);
  } catch (error) {
    console.error('프롬프트 저장 실패:', error);
    saveMessage.value = '❌ 저장 중 오류가 발생했습니다.';
  } finally {
    isSaving.value = false;
  }
};

// Auto-load default prompt on mount (only if current value is empty)
onMounted(async () => {
  if (!props.modelValue && !props.readonly) {
    try {
      const defaultPrompt = await getDefaultPrompt(props.promptKind);
      if (defaultPrompt) {
        emit('update:modelValue', defaultPrompt.promptText);
      }
    } catch (error) {
      console.error('기본 프롬프트 로드 실패:', error);
    }
  }
});
</script>

<template>
  <div>
    <!-- Prompt Editor Card -->
    <Card class="mb-8">
      <Collapsible v-model:open="isOpen">
        <CardHeader>
          <div class="flex items-center justify-between">
            <div>
              <CardTitle>AI 프롬프트</CardTitle>
              <CardDescription>
                {{ readonly ? '자동 생성된 프롬프트입니다.' : 'AI 프롬프트를 확인하거나 수정하세요.' }}
              </CardDescription>
            </div>
            <CollapsibleTrigger as-child>
              <Button variant="ghost" size="sm">
                {{ isOpen ? '접기' : '펼치기' }}
              </Button>
            </CollapsibleTrigger>
          </div>
        </CardHeader>
        <CollapsibleContent>
          <CardContent>
            <textarea
              :value="modelValue"
              @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
              :readonly="readonly"
              class="w-full h-64 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              :class="{ 'bg-gray-50 cursor-not-allowed': readonly }"
              placeholder="AI 프롬프트를 입력하세요..."
            />

            <!-- Current Images Preview -->
            <div v-if="currentImages.length > 0" class="mt-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2">입력 이미지 ({{ currentImages.length }}개)</h4>
              <div class="grid grid-cols-4 gap-2">
                <div
                  v-for="(url, idx) in imagePreviewUrls"
                  :key="idx"
                  class="relative aspect-square rounded-lg border border-gray-200 overflow-hidden"
                >
                  <img
                    :src="url"
                    class="w-full h-full object-cover"
                    alt="Input image"
                  />
                </div>
              </div>
            </div>

            <!-- Save Button (Inside prompt editor) -->
            <div v-if="!readonly" class="mt-4">
              <Button
                @click="handleSavePrompt"
                :disabled="isSaving || !modelValue"
                class="w-full"
                variant="outline"
              >
                {{ isSaving ? '저장 중...' : '💾 현재 프롬프트 저장' }}
              </Button>
              <p v-if="saveMessage" class="mt-2 text-sm text-center" :class="{
                'text-green-600': saveMessage.includes('✅'),
                'text-red-600': saveMessage.includes('❌')
              }">
                {{ saveMessage }}
              </p>
            </div>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  </div>
</template>
