<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- 상단 입력 / 프롬프트 관리 -->
      <div class="grid grid-cols-1 lg:grid-cols-[7fr_3fr] gap-6">
        <!-- 왼쪽 패널 -->
        <Card class="shadow-lg">
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-bold text-gray-900">입력 정보</h2>
              <Button variant="ghost" size="sm" @click="clearImages">초기화</Button>
            </div>

            <!-- 사진 업로드 -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">사진 업로드</label>
              <div
                class="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/50 transition-all"
                @click="triggerFileInput('base')"
              >
                <input
                  ref="baseInput"
                  type="file"
                  accept="image/*"
                  class="hidden"
                  @change="(e) => handleFileSelect(e, 'base')"
                />
                <template v-if="!images.base">
                  <div>
                    <div class="w-14 h-14 mx-auto mb-3 bg-indigo-100 rounded-full flex items-center justify-center">
                      <Upload class="w-6 h-6 text-indigo-600" />
                    </div>
                    <p class="text-gray-700 font-medium text-sm mb-1">클릭하여 사진 업로드</p>
                    <p class="text-xs text-gray-500">정면 사진 권장 (JPG, PNG, 최대 10MB)</p>
                  </div>
                </template>
                <template v-else>
                  <img :src="images.base.preview" class="w-full rounded-lg object-contain max-h-[300px]" alt="Base" />
                </template>
              </div>
            </div>

            <!-- 헤어스타일 선택 -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">헤어스타일 선택</label>
              <div class="grid grid-cols-4 gap-3">
                <div
                  v-for="style in defaultHairStyles"
                  :key="style.id"
                  @click="selectDefaultHair(style.url)"
                  class="border-2 rounded-lg p-2 cursor-pointer transition-all hover:border-indigo-400"
                  :class="{
                    'border-indigo-600 ring-2 ring-indigo-200': selectedDefaultHair === style.url,
                    'border-gray-200': selectedDefaultHair !== style.url
                  }"
                >
                  <div class="aspect-square bg-gray-100 rounded-md mb-1 overflow-hidden">
                    <img :src="style.url" :alt="style.name" class="w-full h-full object-cover" />
                  </div>
                  <p class="text-xs text-center text-gray-600 truncate">{{ style.name }}</p>
                </div>

                <!-- 직접 업로드 -->
                <div
                  class="border-2 border-dashed border-gray-300 rounded-lg p-2 cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/50 transition-all"
                  @click="triggerFileInput('hair')"
                >
                  <input
                    ref="hairInput"
                    type="file"
                    accept="image/*"
                    class="hidden"
                    @change="(e) => handleFileSelect(e, 'hair')"
                  />
                  <template v-if="!images.hair">
                    <div class="aspect-square bg-gray-50 rounded-md flex flex-col items-center justify-center">
                      <div class="w-7 h-7 border-2 border-gray-400 rounded-full flex items-center justify-center mb-1">
                        <span class="text-gray-400 text-base">+</span>
                      </div>
                    </div>
                  </template>

                  <template v-else>
                    <div class="aspect-square bg-gray-100 rounded-md mb-1 overflow-hidden">
                      <img :src="images.hair.preview" alt="Custom" class="w-full h-full object-cover" />
                    </div>
                  </template>

                  <p class="text-xs text-center text-gray-600">직접 업로드</p>
                </div>
              </div>
            </div>

            <!-- 합성 버튼 -->
            <Button
              class="w-full bg-indigo-600 hover:bg-indigo-700 mt-4"
              :disabled="!allImagesUploaded || isProcessing"
              @click="generateCombinedImage"
            >
              <Sparkles class="w-4 h-4 mr-2" />
              {{ isProcessing ? "처리중..." : "AI 합성하기" }}
            </Button>
            <p class="text-center text-xs text-gray-500 mt-2">평균 처리 시간: 5~10초</p>
          </div>
        </Card>

        <!-- 오른쪽 패널 -->
        <Card class="shadow-lg">
          <div class="p-5">
            <h2 class="text-lg font-bold text-gray-900 mb-3">프롬프트 관리</h2>
            <div class="space-y-4 max-h-[400px] overflow-auto">
              <PromptEditor
                v-model="aiPrompt"
                :prompt-kind="promptKind"
                model-kind="gemini-2.5-flash"
                :readonly="false"
              />
              <PromptManagement
                v-model="aiPrompt"
                :prompt-kind="promptKind"
              />
            </div>
          </div>
        </Card>
      </div>

      <!-- 결과 비교 -->
<Card class="shadow-lg">
  <div class="p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold text-gray-900">결과 비교</h2>
      <div class="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          :disabled="!result"
          @click="regenerateImage"
        >
          재생성
        </Button>
        <Button
          size="sm"
          class="bg-indigo-600 hover:bg-indigo-700"
          :disabled="!result"
          @click="downloadImage"
        >
          다운로드
        </Button>
      </div>
    </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- 합성 전 -->
            <div class="relative">
              <div class="absolute top-2 left-2 bg-gray-900/80 text-white px-3 py-1 rounded-full text-xs font-medium z-10">
                합성 전
              </div>
              <div class="aspect-[2/3] bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                <img v-if="images.base" :src="images.base.preview" class="w-full h-full object-cover" />
                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                  원본 이미지를 업로드하세요
                </div>
              </div>
            </div>

            <!-- 합성 후 -->
            <div class="relative">
              <div class="absolute top-2 left-2 bg-indigo-600 text-white px-3 py-1 rounded-full text-xs font-medium z-10">
                합성 후
              </div>
              <div class="aspect-[2/3] bg-gray-100 rounded-lg overflow-hidden border-2 border-indigo-200">
                <div v-if="isProcessing" class="w-full h-full flex flex-col items-center justify-center">
                  <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-2"></div>
                  <p class="text-gray-600 text-sm font-medium">이미지 합성 중...</p>
                </div>
                <div v-else-if="error" class="w-full h-full flex flex-col items-center justify-center p-4">
                  <p class="text-red-600 mb-2 text-sm">{{ error }}</p>
                  <Button @click="generateCombinedImage" size="xs" variant="outline">다시 시도</Button>
                </div>
                <img v-else-if="result" :src="result" class="w-full h-full object-cover" />
                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                  합성 결과가 여기에 표시됩니다
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, reactive, computed } from "vue"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, Sparkles } from "lucide-vue-next"
import PromptEditor from "@/components/bangkku/PromptEditor.vue"
import PromptManagement from "@/components/bangkku/PromptManagement.vue"
import { processMultipleImagesWithGeminiV2 } from "@/services/bangkku/gemini.service"

// 기본 헤어스타일 이미지 (3종)
import hairStyle1 from "@/assets/hair-default/hair1.png"
import hairStyle2 from "@/assets/hair-default/hair2.png"
import hairStyle3 from "@/assets/hair-default/hair3.png"

interface ImageData {
  file: File
  preview: string
}

const baseInput = ref<HTMLInputElement | null>(null)
const hairInput = ref<HTMLInputElement | null>(null)

const images = reactive<{ base: ImageData | null; hair: ImageData | null }>({
  base: null,
  hair: null,
})

const isProcessing = ref(false)
const result = ref<string | null>(null)
const error = ref<string | null>(null)
const useDefaultHair = ref(false)
const selectedDefaultHair = ref<string | null>(null)

// PromptEditor + PromptManagement
const aiPrompt = ref(`당신은 세계 최고 수준의 전문 이미지 합성가입니다.
지금부터 두 장의 이미지를 기반으로 단 하나의 완성된 이미지를 생성해야 합니다.

1️⃣ 첫 번째 이미지는 인물의 정면 또는 측면 사진입니다.  
2️⃣ 두 번째 이미지는 적용할 헤어스타일의 이미지입니다.

작업 지시:
- 두 번째 이미지의 머리카락 형태, 질감, 색상을 분석하여 첫 번째 인물의 머리에 **정확히 맞게 합성**하세요.  
- 머리카락 경계선을 자연스럽게 블렌딩하고, 머리 형태와 방향을 인물의 각도에 맞게 조정하세요.  
- 조명, 노출, 피부 톤, 배경의 색상 균형을 **완벽히 일치**시켜 위화감이 전혀 없도록 하세요.  
- 불필요한 텍스트, 로고, 장식, 원본 이미지의 흔적은 절대 남기지 마세요.  
- 기존 이미지를 그대로 복제하거나 단순히 덮어쓰지 말고, **두 이미지를 참고해 완전히 새로운 합성 이미지**를 생성하세요.

출력 조건:
- 오직 **최종 합성된 인물 이미지 하나만** 생성합니다.  
- 어떠한 텍스트, 워터마크, 프레임, 배경 설명도 포함하지 않습니다.  
- 출력 이미지는 고해상도이며, 현실적인 디테일과 자연스러운 질감을 유지해야 합니다.

지금부터 이 지시를 기반으로 최고의 결과물을 만들어주세요.
`);



// Prompt 관리 종류 지정
const promptKind = "bangkku/hair-combine"

// 기본 헤어스타일 목록
const defaultHairStyles = [
  { id: 1, name: "짧은 헤어", url: hairStyle1 },
  { id: 2, name: "세미 롱", url: hairStyle2 },
  { id: 3, name: "웨이브 롱", url: hairStyle3 },
]

// 파일 업로드
const triggerFileInput = (key: "base" | "hair") => {
  if (key === "base") baseInput.value?.click()
  else hairInput.value?.click()
}

const handleFileSelect = (event: Event, key: "base" | "hair") => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file && file.type.startsWith("image/")) {
    if (images[key]) URL.revokeObjectURL(images[key]!.preview)
    images[key] = { file, preview: URL.createObjectURL(file) }
    if (key === "hair") {
      useDefaultHair.value = false
      selectedDefaultHair.value = null
    }
  }
}

// 기본 헤어스타일 선택
const selectDefaultHair = async (hairUrl: string) => {
  try {
    const response = await fetch(hairUrl)
    const blob = await response.blob()
    const file = new File([blob], "default-hair.png", { type: blob.type })
    images.hair = { file, preview: hairUrl }
    useDefaultHair.value = true
    selectedDefaultHair.value = hairUrl
  } catch (err) {
    console.error("기본 헤어스타일 로드 실패:", err)
  }
}

// 초기화
const clearImages = () => {
  images.base = null
  images.hair = null
  result.value = null
  error.value = null
  useDefaultHair.value = false
  selectedDefaultHair.value = null
  if (baseInput.value) baseInput.value.value = ""
  if (hairInput.value) hairInput.value.value = ""
}

// 업로드 상태
const allImagesUploaded = computed(() => images.base && images.hair)

// 이미지 합성
const generateCombinedImage = async () => {
  if (!allImagesUploaded.value) return
  isProcessing.value = true
  result.value = null
  error.value = null
  try {
    const imageFiles = [images.base!.file, images.hair!.file];
    console.log("imageFiles", imageFiles);
    console.log("imageFiles", imageFiles);
    // const { editedUrl } = await processMultipleImagesWithGemini({
    const { editedUrl } = await processMultipleImagesWithGeminiV2({
      prompt: aiPrompt.value,
      imageFiles,
    })
    result.value = editedUrl
  } catch (err) {
    console.error("이미지 합성 실패:", err)
    error.value = "이미지 합성 중 오류가 발생했습니다."
  } finally {
    isProcessing.value = false
  }
}

// 재생성 (마지막 조건 그대로 다시 실행)
const regenerateImage = async () => {
  if (!images.base || !images.hair) return;
  await generateCombinedImage();
};

// 다운로드 (Blob 변환 후 a태그 트리거)
const downloadImage = () => {
  if (!result.value) return;

  const link = document.createElement("a");
  link.href = result.value;
  link.download = "combined-image.png";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>
