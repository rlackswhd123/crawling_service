<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from "vue"
import { Sparkles, Download, ImageIcon, PlayCircle } from "lucide-vue-next"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { processShowroomGenerationWithGemini, generateCopywritingForShowroom } from "@/services/showroom/gemini.service"
import { veo3Service } from "@/services/showroom/veo3.service"

// -----------------------------------------------------
// 🖼️ 기본 이미지 (목업용)
// -----------------------------------------------------
import defaultProduct1 from "@/assets/showroom-default/default_product1.png"
import defaultProduct2 from "@/assets/showroom-default/default_product2.png"
import defaultProduct3 from "@/assets/showroom-default/default_product3.png"
import defaultReference from "@/assets/showroom-default/default_reference1.png"

// -----------------------------------------------------
// 🌈 스크롤바 스타일
// -----------------------------------------------------
onMounted(() => {
  const style = document.createElement("style")
  style.textContent = `
    .scrollbar-thin::-webkit-scrollbar { height: 6px; }
    .scrollbar-thin::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
  `
  document.head.appendChild(style)
})

// -----------------------------------------------------
// 🧩 상태 변수
// -----------------------------------------------------
const brand = ref("")
const description = ref("")
const background = ref("")
const place = ref("none")
const customPlace = ref("")
const time = ref("none")
const season = ref("none")
const weather = ref("none")
const usage = ref("personal")
const music = ref("")
const story = ref("")
const cameraPath = ref("")
const imageRatio = ref("1:1")
const videoQuality = ref("720p")
const directingNotes = ref("")

const productImages = ref<string[]>([])
const referenceImages = ref<string[]>([])
const images = ref<string[]>([])
const videos = ref<string[]>([])
const videoCaptions = ref<string[]>([])

const isLoading = ref(false)
const isCopyLoading = ref(false)
const isVideoGenerating = ref(false)
const loadingIndices = ref<number[]>([])
const videoProgress = ref(0)
const videoStatus = ref("")
const showModal = ref(false)
const showVideoModal = ref(false)
const currentImage = ref(0)


const modelInfo = computed(() => modelSettings.value.slice(0, Number(personCount.value)))


// -----------------------------------------------------
// 👩‍🦰 모델 설정
// -----------------------------------------------------
const personCount = ref("0")
const modelSettings = ref([
  { gender: "", age: "", clothing: "", clothingCustom: "", relation: "" },
  { gender: "", age: "", clothing: "", clothingCustom: "", relation: "" },
  { gender: "", age: "", clothing: "", clothingCustom: "", relation: "" },
])

// -----------------------------------------------------
// 💡 이미지 각도명
// -----------------------------------------------------
const cameraAngles = [
  "정면 구도",
  "측면 구도",
  "광각 구도",
  "후면 구도",
]

// -----------------------------------------------------
// 🧩 이미지별 카피라이트 저장
// -----------------------------------------------------
interface ImageCaption {
  title: string
  description: string
}
const imageCaptions = ref<ImageCaption[]>([
  { title: "", description: "" },
  { title: "", description: "" },
  { title: "", description: "" },
  { title: "", description: "" },
])

// -----------------------------------------------------
// 🖼️ 이미지 업로드
// -----------------------------------------------------
const handleFileUpload = (targetList: any) => {
  const input = document.createElement("input")
  input.type = "file"
  input.accept = "image/*"
  input.multiple = true
  input.onchange = (e: any) => {
    const files = e.target.files
    if (files.length) {
      Array.from(files).forEach((file: File) => {
        const reader = new FileReader()
        reader.onload = (ev) => targetList.value.push(ev.target?.result as string)
        reader.readAsDataURL(file)
      })
    }
  }
  input.click()
}
const addProductImage = () => handleFileUpload(productImages)
const addReferenceImage = () => handleFileUpload(referenceImages)
const removeProductImage = (i: number) => productImages.value.splice(i, 1)
const removeReferenceImage = (i: number) => referenceImages.value.splice(i, 1)

// -----------------------------------------------------
// 🧠 프롬프트 구성 함수
// -----------------------------------------------------
const buildGeminiPrompt = (angle: string) => {
  const activePlace = place.value === "custom" ? customPlace.value : place.value

  const modelDesc =
    personCount.value === "0"
      ? "모델 없이 제품 중심 구도"
      : modelSettings.value
          .slice(0, Number(personCount.value))
          .map(
            (m, idx) =>
              `모델 ${idx + 1}: ${m.gender || "성별 미정"}, ${
                m.age || "나이 미정"
              }, 복장: ${m.clothing === "custom" ? m.clothingCustom : m.clothing || "기본 복장"}, 관계: ${
                m.relation || "주인공"
              }`
          )
          .join("\n")

  const ratioMap: Record<string, string> = {
    "1:1": "정사각형",
    "16:9": "와이드 (풍경형)",
    "4:3": "표준",
    "3:4": "세로형",
    "9:16": "스토리 비율",
  }

  return `
당신은 시네마틱 영상 및 사진을 디자인하는 아트 디렉터입니다.
아래 정보를 기반으로 ${brand.value} 제품의 프리미엄 쇼룸 이미지를 ${angle} 시점에서 생성하세요.

📦 제품 설명:
${description.value || "설명 없음"}

🎬 연출 정보:
- 장소: ${activePlace}
- 배경: ${background.value || "기본"}
- 시간: ${time.value}
- 계절: ${season.value}
- 날씨: ${weather.value}
- 카메라 구도: ${angle}
- 카메라 동선: ${cameraPath.value}
- 이미지 비율: ${ratioMap[imageRatio.value] || imageRatio.value}
- 영상 해상도: ${videoQuality.value}
- 음악/분위기: ${music.value || "감성적, 잔잔한 톤"}
- 스토리/시나리오: ${story.value || "제품 중심의 감성적 장면"}
- 연출 노트: ${directingNotes.value || "자연스럽고 세련된 조명"}
  
👥 모델 구성:
${modelDesc}

⚠️ 주의사항:
- 텍스트, 로고, 워터마크 금지
- 제품이 중심(Main focus)
- ${angle} 시점 강조
- 부드러운 빛과 자연스러운 카메라 연출
`
}

// -----------------------------------------------------
// 🤖 Gemini 기반 이미지 + 카피 + 비디오 생성
// -----------------------------------------------------
const generateAI = async () => {
  try {
    isLoading.value = true
    isCopyLoading.value = true
    images.value = []
    imageCaptions.value = []
    loadingIndices.value = [0, 1, 2, 3]

    console.log("🎬 쇼룸용 이미지 생성 시작")

    // ✅ Gemini 서비스 한 번 호출 (내부에서 4구도 자동 생성)
    const result = await processShowroomGenerationWithGemini({
      brand: brand.value,
      description: description.value,
      background: background.value,
      place: place.value,
      time: time.value,
      season: season.value,
      weather: weather.value,
      usage: usage.value,
      music: music.value,
      story: story.value,
      modelInfo: modelInfo.value,
      productImages: productImages.value,
      referenceImages: referenceImages.value,
    })


    if (result.images && result.images.length > 0) {
      // ✅ 1️⃣ 이미지 먼저 표시
      images.value = result.images
      console.log(`✅ ${result.images.length}장 이미지 생성 완료`)

      // ✅ 2️⃣ 화면 렌더링 완료를 기다림
      await nextTick()

      // ✅ 3️⃣ 이후 카피라이트 비동기 처리
      for (let i = 0; i < result.images.length; i++) {
        generateCopywritingForShowroom({
          prompt: description.value,
          imageAngle: ["정면 구도", "측면 구도", "광각 구도", "후면 구도"][i],
          brand: brand.value,
        }).then((copy) => {
          imageCaptions.value[i] = {
            title: copy.title,
            description: copy.description,
          }
          loadingIndices.value = loadingIndices.value.filter((idx) => idx !== i)
        })
      }
    }


    // ✅ 모든 이미지 base64 로드 완료 보장
    console.log("🕓 모든 이미지 base64 로드 대기 중...")
    await nextTick()
    await new Promise<void>((resolve) => {
      // 0.5초 정도 딜레이를 줘서 FileReader 비동기 로딩 완료 보장
      setTimeout(() => {
        console.log("✅ 이미지 로드 완료 — 영상 생성 시작")
        resolve()
      }, 500)
    })

    // ✅ 모든 이미지 완료 후 영상 자동 생성
    if (images.value.length > 0 && images.value.every((img) => img.startsWith("data:image"))) {
      await generateVideoFromImages(images.value)
    } else {
      console.warn("⚠️ 이미지가 완전히 로드되지 않아 영상 생성을 건너뜁니다.")
      console.log("현재 images 상태:", images.value)
    }

    isCopyLoading.value = false
    isLoading.value = false
  } catch (err) {
    console.error("❌ AI 생성 오류:", err)
    alert("AI 콘텐츠 생성 중 오류가 발생했습니다.")
    isLoading.value = false
    isCopyLoading.value = false
  }
}





// -----------------------------------------------------
// 🎬 Veo3 영상 생성
// -----------------------------------------------------
// const generateVideoFromImages = async (list: string[]) => {
//   try {
//     if (!list || list.length === 0) {
//       alert("영상 생성을 위한 이미지가 없습니다.")
//       return
//     }

//     isVideoGenerating.value = true
//     videoProgress.value = 0
//     videoStatus.value = "영상 생성 준비 중..."

//     // const cleanBase64Images = list.map((img) =>
//     //   img.replace(/^data:image\/\w+;base64,/, "")
//     // )
//   const cleanBase64Images = list
//   console.log("전달하는 images", cleanBase64Images)

//   const cleanImage = cleanBase64Images[0].replace(/^data:image\/\w+;base64,/, "")


  

//     await veo3Service.generateShowroomVideo(
//       {
//         brand: brand.value,
//         description: description.value,
//         background: background.value,
//         place: place.value,
//         time: time.value,
//         season: season.value,
//         weather: weather.value,
//         usage: usage.value,
//         music: music.value,
//         story: story.value,
//         cameraPath: cameraPath.value,
//         imageRatio: imageRatio.value,
//         videoQuality: videoQuality.value,
//         directingNotes: directingNotes.value,
//         // image: cleanBase64Images[0],
//         image: cleanImage,
//       },
//       {
//         onProgress: (p, msg) => {
//           videoProgress.value = p
//           videoStatus.value = msg || "영상 생성 중..."
//         },
//         onCompleted: (r) => {
//           videos.value = [r.video_url]
//           videoStatus.value = "영상 생성 완료 ✅"
//           isVideoGenerating.value = false
//         },
//         onError: (e) => {
//           console.error("❌ 비디오 생성 실패:", e)
//           alert("비디오 생성 실패: " + e)
//           isVideoGenerating.value = false
//         },
//       }
//     )
//   } catch (err) {
//     console.error("❌ 영상 생성 오류:", err)
//     alert("영상 생성 오류 발생: " + err)
//     isVideoGenerating.value = false
//   }
// }

const generateVideoFromImages = async (list: string[]) => {
  try {
    if (!list || list.length === 0) {
      alert("영상 생성을 위한 이미지가 없습니다.")
      return
    }

    isVideoGenerating.value = true
    videoProgress.value = 0
    videoStatus.value = "영상 생성 준비 중..."

    // Base64 처리 (그대로 유지)
    const cleanBase64Images = list
    const cleanImage = cleanBase64Images[0] // 첫 번째 이미지 사용

    // ✅ Veo용 프롬프트 — 간결하게 문자열로 전달
    const prompt = `
      ${brand.value} 브랜드의 ${description.value} 제품을 중심으로 한 시네마틱 쇼룸 영상.
      장면은 ${place.value} 공간에서 ${season.value} ${time.value}대의 ${weather.value} 분위기 속에 전개된다.
      ${cameraPath.value} 카메라 동선으로 부드럽게 이동하며, ${videoQuality.value} 화질로 표현된다.
      영상은 사실적이고 감성적인 무드로 구성되며, 텍스트나 로고는 포함되지 않는다.
    `.trim()

    // ✅ 기존에 잘 작동하는 generateVideo() 그대로 사용
    await veo3Service.generateVideo(
      {
        prompt,
        image: cleanImage,
      },
      {
        onProgress: (p, msg) => {
          videoProgress.value = p
          videoStatus.value = msg || "영상 생성 중..."
        },
        onCompleted: (r) => {
          videos.value = [r.video_url]
          videoStatus.value = "영상 생성 완료 ✅"
          isVideoGenerating.value = false
        },
        onError: (e) => {
          console.error("❌ 비디오 생성 실패:", e)
          alert("비디오 생성 실패: " + e)
          isVideoGenerating.value = false
        },
      }
    )
  } catch (err) {
    console.error("❌ 영상 생성 오류:", err)
    alert("영상 생성 오류 발생: " + err)
    isVideoGenerating.value = false
  }
}


// -----------------------------------------------------
// 🖼️ 이미지 모달
// -----------------------------------------------------
const openModal = (i: number) => {
  if (!images.value[i]) return
  currentImage.value = i
  showModal.value = true
}
const closeModal = () => (showModal.value = false)
const prevImage = () =>
  (currentImage.value = (currentImage.value - 1 + images.value.length) % images.value.length)
const nextImage = () =>
  (currentImage.value = (currentImage.value + 1) % images.value.length)
const openVideoModal = () => (videos.value.length ? (showVideoModal.value = true) : null)
const closeVideoModal = () => (showVideoModal.value = false)

// -----------------------------------------------------
// 💾 다운로드
// -----------------------------------------------------
const downloadImage = (img: string, idx: number) => {
  const a = document.createElement("a")
  a.href = img
  a.download = `${brand.value}_${idx + 1}.png`
  a.click()
}
const downloadAllImages = () => images.value.forEach((img, idx) => downloadImage(img, idx))

// -----------------------------------------------------
// 📋 복사 기능
// -----------------------------------------------------
const copyCaption = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    const div = document.createElement("div")
    div.textContent = "복사되었습니다 ✅"
    Object.assign(div.style, {
      position: "fixed",
      bottom: "30px",
      right: "30px",
      background: "rgba(0,0,0,0.8)",
      color: "#fff",
      padding: "8px 14px",
      borderRadius: "8px",
      fontSize: "12px",
      zIndex: "9999",
      transition: "opacity 0.3s",
    })
    document.body.appendChild(div)
    setTimeout(() => (div.style.opacity = "0"), 1200)
    setTimeout(() => div.remove(), 1500)
  } catch {
    alert("복사 실패! 브라우저 권한을 확인해주세요.")
  }
}

// -----------------------------------------------------
// 🧩 목업 데이터
// -----------------------------------------------------
async function toBase64(url: string): Promise<string> {
  const res = await fetch(url)
  const blob = await res.blob()
  return new Promise<string>((resolve) => {
    const reader = new FileReader()
    reader.onloadend = () => resolve((reader.result as string).split(",")[1])
    reader.readAsDataURL(blob)
  })
}

const fillMockData = async () => {
  brand.value = "AURORA"
  description.value = "은은한 불빛과 따뜻한 향으로 공간을 감싸는 감성 캔들. 하루의 피로를 녹이는 힐링 무드."
  background.value = "따뜻한 톤의 실내 조명 아래, 미니멀한 인테리어 공간"
  place.value = "office"
  customPlace.value = ""
  time.value = "evening"
  season.value = "winter"
  weather.value = "snowy"
  usage.value = "commercial"
  music.value = "잔잔한 피아노와 따뜻한 현악기"
  story.value = "눈 내리는 겨울 저녁, 오피스에서 퇴근 후 혼자만의 시간을 즐기며 캔들을 켜는 감성적인 장면"
  cameraPath.value = "pan-right"
  imageRatio.value = "16:9"
  videoQuality.value = "1080p"
  directingNotes.value =
    "제품이 중심에 위치하고 부드러운 보케 효과와 따뜻한 오렌지 조명으로 연출. 배경은 은은하게 흐릿하게 처리."

    // ✅ 모델 설정 (스크린샷과 동일)
    personCount.value = "3"
  modelSettings.value = [
    {
      gender: "female",
      age: "20s",
      clothing: "casual",
      clothingCustom: "",
      relation: "main",
    },
    {
      gender: "male",
      age: "20s",
      clothing: "sportswear",
      clothingCustom: "",
      relation: "lover",
    },
    {
      gender: "female",
      age: "under10",
      clothing: "sportswear",
      clothingCustom: "",
      relation: "family",
    },
  ]

  const [p1, p2, p3, ref] = await Promise.all([
    toBase64(defaultProduct1),
    toBase64(defaultProduct2),
    toBase64(defaultProduct3),
    toBase64(defaultReference),
  ])

  productImages.value = [
    `data:image/png;base64,${p1}`,
    `data:image/png;base64,${p2}`,
    `data:image/png;base64,${p3}`,
  ]
  referenceImages.value = [`data:image/png;base64,${ref}`]
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <main class="max-w-[1400px] mx-auto px-6 py-8">
      <div class="grid lg:grid-cols-2 gap-6">
        <!-- 왼쪽 패널 -->
        <Card class="shadow-sm flex flex-col justify-between">
          <div>
            <CardHeader class="relative flex items-start justify-between mb-2 px-0 pt-0 pb-2">
              <div class="flex justify-between items-start w-full ">
                <div class="flex flex-col gap-1.5">
                  <CardTitle class="text-lg font-semibold">쇼룸 생성</CardTitle>
                  <CardDescription class="text-sm text-gray-500">
                    AI 쇼룸 콘텐츠 생성 옵션을 설정합니다.
                  </CardDescription>
                </div>
              </div>

              <!-- ✅ 버튼을 CardHeader의 가장 우측으로 절대 위치 -->
              <Button
                class="h-7 px-3 text-xs absolute top-2 right-6 bg-indigo-600 text-white hover:bg-indigo-700"
                @click="fillMockData"
              >
                빈칸 채우기
              </Button>
            </CardHeader>


            <CardContent class="space-y-4 text-xs">
              
              <!-- ✅ 제품명 / 설명 -->
              <div class="space-y-2">
                <div class="grid grid-cols-[60px_1fr] items-center gap-2">
                  <Label>제품명</Label>
                  <Input v-model="brand" placeholder="제품명을 입력하세요" />
                </div>

                <div class="grid grid-cols-[60px_1fr] items-start gap-2">
                  <Label class="pt-1.5">설명</Label>
                  <Textarea v-model="description" class="min-h-[60px] resize-none" placeholder="제품 설명을 입력하세요" />
                </div>
              </div>
              
              <!-- ✅ 제품 / 참고 이미지 (50:50, overflow-x-scroll) -->
              <div class="space-y-2 ">
                <div class="flex gap-4">
                  <!-- 제품 이미지 -->
                  <div class="flex-1">
                    <Label class="font-semibold">제품 이미지</Label>
                    <div class="flex overflow-x-auto scrollbar-thin gap-2 p-2 border rounded-md bg-white">
                      <div
                        v-for="(img, i) in productImages"
                        :key="'prod-'+i"
                        class="relative flex-shrink-0 w-20 h-20 rounded border overflow-hidden group"
                      >
                        <img :src="img" class="w-full h-full object-cover" />
                        <button
                          @click="removeProductImage(i)"
                          class="absolute top-0 right-0 bg-black/60 text-white text-[10px] px-1 rounded-bl opacity-0 group-hover:opacity-100 transition"
                        >✕</button>
                      </div>
                      <button
                        class="flex-shrink-0 w-20 h-20 border rounded-lg flex items-center justify-center text-gray-400 hover:text-indigo-600"
                        @click="addProductImage"
                      >＋</button>
                    </div>
                  </div>

                  <!-- 참고 이미지 -->
                  <div class="flex-1">
                    <Label class="font-semibold">참고 이미지</Label>
                    <div class="flex overflow-x-auto scrollbar-thin gap-2 p-2 border rounded-md bg-white">
                      <div
                        v-for="(img, i) in referenceImages"
                        :key="'ref-'+i"
                        class="relative flex-shrink-0 w-20 h-20 rounded border overflow-hidden group"
                      >
                        <img :src="img" class="w-full h-full object-cover" />
                        <button
                          @click="removeReferenceImage(i)"
                          class="absolute top-0 right-0 bg-black/60 text-white text-[10px] px-1 rounded-bl opacity-0 group-hover:opacity-100 transition"
                        >✕</button>
                      </div>
                      <button
                        class="flex-shrink-0 w-20 h-20 border rounded-lg flex items-center justify-center text-gray-400 hover:text-indigo-600"
                        @click="addReferenceImage"
                      >＋</button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="w-full border-b border-gray-300 my-4"></div>


              <!-- ✅ 촬영 정보 (직접입력 추가) -->
              <div>
                <Label class="font-semibold mb-1 block">촬영 정보</Label>
                <div class="flex flex-wrap gap-2 items-center">
                  <div class="flex items-center gap-2">
                    <Select v-model="place">
                      <SelectTrigger class="h-8 w-[90px] text-xs"><SelectValue placeholder="장소" /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="office">사무실</SelectItem>
                        <SelectItem value="camping">캠핑</SelectItem>
                        <SelectItem value="living">거실</SelectItem>
                        <SelectItem value="bedroom">침실</SelectItem>
                        <SelectItem value="custom">직접입력</SelectItem>
                      </SelectContent>
                    </Select>
                    <!-- ✅ 장소 직접입력 -->
                    <Input
                      v-if="place === 'custom'"
                      v-model="customPlace"
                      placeholder="직접 입력"
                      class="h-8 w-[150px] text-xs"
                    />
                  </div>

                  <Select v-model="season">
                    <SelectTrigger class="h-8 w-[90px] text-xs"><SelectValue placeholder="계절" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="spring">봄</SelectItem>
                      <SelectItem value="summer">여름</SelectItem>
                      <SelectItem value="fall">가을</SelectItem>
                      <SelectItem value="winter">겨울</SelectItem>
                    </SelectContent>
                  </Select>

                  <Select v-model="time">
                    <SelectTrigger class="h-8 w-[90px] text-xs"><SelectValue placeholder="시간" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="morning">아침</SelectItem>
                      <SelectItem value="evening">저녁</SelectItem>
                      <SelectItem value="night">밤</SelectItem>
                      <SelectItem value="sunset">노을</SelectItem>
                    </SelectContent>
                  </Select>

                  <Select v-model="weather">
                    <SelectTrigger class="h-8 w-[90px] text-xs"><SelectValue placeholder="날씨" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sunny">맑음</SelectItem>
                      <SelectItem value="rainy">비</SelectItem>
                      <SelectItem value="cloudy">흐림</SelectItem>
                      <SelectItem value="snowy">눈</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <!-- ✅ 모델 설정 (나이: 10대 이하 추가, 복장: 직접입력 추가) -->
              <div>
                <Label class="font-semibold block mb-1">모델 설정</Label>

                <Select v-model="personCount">
                  <SelectTrigger class="h-8 text-xs w-full"><SelectValue placeholder="모델 인원" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">없음</SelectItem>
                    <SelectItem value="1">1인</SelectItem>
                    <SelectItem value="2">2인</SelectItem>
                    <SelectItem value="3">3인</SelectItem>
                    <SelectItem value="multi">다수</SelectItem>
                  </SelectContent>
                </Select>

                <div v-if="personCount !== '0'" class="mt-2 space-y-3">
                  <template v-if="['1','2','3'].includes(personCount)">
                    <div v-for="n in Number(personCount)" :key="'model-'+n" class="border rounded-md p-2 bg-gray-50">
                      <Label class="text-xs font-semibold text-gray-700 block mb-1">모델 {{ n }}</Label>
                      <div class="flex flex-wrap gap-2 items-center">
                        <!-- 성별 -->
                        <Select v-model="modelSettings[n-1].gender" class="w-[90px]">
                          <SelectTrigger class="h-8 text-xs"><SelectValue placeholder="성별" /></SelectTrigger>
                          <SelectContent><SelectItem value="male">남성</SelectItem><SelectItem value="female">여성</SelectItem></SelectContent>
                        </Select>

                        <!-- ✅ 나이대에 10대 이하 추가 -->
                        <Select v-model="modelSettings[n-1].age" class="w-[90px]">
                          <SelectTrigger class="h-8 text-xs"><SelectValue placeholder="나이" /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="under10">10대 이하</SelectItem>
                            <SelectItem value="10s">10대</SelectItem>
                            <SelectItem value="20s">20대</SelectItem>
                            <SelectItem value="30s">30대</SelectItem>
                            <SelectItem value="40s+">40대+</SelectItem>
                          </SelectContent>
                        </Select>

                        <!-- ✅ 복장 직접입력 -->
                        <div class="flex items-center gap-2">
                          <Select v-model="modelSettings[n-1].clothing" class="w-[90px]">
                            <SelectTrigger class="h-8 text-xs"><SelectValue placeholder="복장" /></SelectTrigger>
                            <SelectContent>
                              <SelectItem value="casual">캐주얼</SelectItem>
                              <SelectItem value="formal">정장</SelectItem>
                              <SelectItem value="sportswear">운동복</SelectItem>
                              <SelectItem value="custom">직접입력</SelectItem>
                            </SelectContent>
                          </Select>
                          <Input
                            v-if="modelSettings[n-1].clothing === 'custom'"
                            v-model="modelSettings[n-1].clothingCustom"
                            placeholder="복장 입력"
                            class="h-8 w-[120px] text-xs"
                          />
                        </div>

                        <!-- 관계 -->
                        <Select v-model="modelSettings[n-1].relation" class="w-[90px]">
                          <SelectTrigger class="h-8 text-xs"><SelectValue placeholder="관계" /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="main">주인공</SelectItem>
                            <SelectItem value="lover">애인</SelectItem>
                            <SelectItem value="friend">친구</SelectItem>
                            <SelectItem value="colleague">동료</SelectItem>
                            <SelectItem value="family">가족</SelectItem>
                            <SelectItem value="stranger">모르는 사람</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </template>
                </div>
              </div>

              <!-- ✅ 카메라 동선 / 이미지 / 영상 사이즈 (한 줄 배치) -->
              <div class="flex flex-wrap gap-2 items-center">
                <div class="flex-1 min-w-[150px]">
                  <Label class="font-semibold">카메라 동선</Label>
                  <Select v-model="cameraPath">
                    <SelectTrigger class="h-8 text-xs"><SelectValue placeholder="움직임 선택" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pan-left">좌 → 우 이동</SelectItem>
                      <SelectItem value="pan-right">우 → 좌 이동</SelectItem>
                      <SelectItem value="zoom-in">줌 인 (가까워짐)</SelectItem>
                      <SelectItem value="zoom-out">줌 아웃 (멀어짐)</SelectItem>
                      <SelectItem value="orbit">주변 궤도 이동</SelectItem>
                      <SelectItem value="focus-shift">초점 이동 (피사체 전환)</SelectItem>
                      <SelectItem value="fixed">고정 앵글</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div class="flex-1 min-w-[150px]">
                  <Label class="font-semibold">이미지 비율</Label>
                  <Select v-model="imageRatio">
                    <SelectTrigger class="h-8 text-xs"><SelectValue placeholder="비율 선택" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1:1">1:1 (정사각형)</SelectItem>
                      <SelectItem value="16:9">16:9 (와이드)</SelectItem>
                      <SelectItem value="4:3">4:3 (표준)</SelectItem>
                      <SelectItem value="3:4">3:4 (세로형)</SelectItem>
                      <SelectItem value="9:16">9:16 (스토리)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div class="flex-1 min-w-[150px]">
                  <Label class="font-semibold">영상 해상도</Label>
                  <Select v-model="videoQuality">
                    <SelectTrigger class="h-8 text-xs"><SelectValue placeholder="해상도" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="720p">720p (HD)</SelectItem>
                      <SelectItem value="1080p">1080p (Full HD)</SelectItem>
                      <SelectItem value="4K">4K (Ultra HD)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div class="w-full border-b border-gray-300 my-4"></div>

              <!-- ✅ 연출 지시 -->
              <div>
                <Label class="font-semibold">연출 지시</Label>
                <Textarea
                  v-model="directingNotes"
                  class="min-h-[80px] text-xs resize-none"
                  placeholder="추가로 입력할 원하는 분위기, 조명, 카메라 연출 등을 입력하세요."
                />
              </div>
            </CardContent>
          </div>

          <div class="p-4 border-t border-gray-100">
            <Button
              class="w-full bg-indigo-600 hover:bg-indigo-700 text-white h-10 text-sm font-medium"
              @click="generateAI"
            >
              <Sparkles class="w-4 h-4 mr-2" />
              AI 콘텐츠 생성하기
            </Button>
          </div>
        </Card>

        <!-- 오른쪽 패널 -->
        <Card class="shadow-sm flex flex-col justify-between">
          <CardHeader class="mb-[15px]">
            <CardTitle class="text-xl">생성 결과</CardTitle>
            <CardDescription>
              AI가 생성한 4가지 구도의 쇼룸 이미지를 확인하고, 각각의 카피라이트를 검토하세요.
            </CardDescription>
          </CardHeader>

          <CardContent class="space-y-6">
            <!-- 🖼️ 이미지 섹션 -->
            <div>
              <div class="flex items-center gap-2 text-sm font-medium mb-3">
                <ImageIcon class="w-4 h-4 text-indigo-600" />
                <span>생성된 이미지 ({{ images.length }}/4)</span>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div
                  v-for="(_, i) in 4"
                  :key="i"
                  class="bg-gray-50 rounded-lg border p-3 flex flex-col gap-3 shadow-sm"
                >
                  <!-- 각도명 -->
                  <div class="flex justify-between items-center">
                    <span class="text-sm font-semibold text-gray-800">
                      {{ cameraAngles[i] || `각도 ${i + 1}` }}
                    </span>
                    <button
                      v-if="images[i]"
                      @click.stop="downloadImage(images[i]!, i)"
                      class="text-xs text-indigo-600 hover:underline"
                    >
                      다운로드
                    </button>
                  </div>

                  <!-- 이미지 -->
                  <div
                    class="relative aspect-square bg-gray-100 rounded-md overflow-hidden flex items-center justify-center cursor-pointer"
                    @click="openModal(i)"
                  >
                    <template v-if="loadingIndices.includes(i)">
                      <div class="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    </template>

                    <template v-else-if="images[i]">
                      <img :src="images[i] || ''" class="w-full h-full object-cover" />
                    </template>

                    <template v-else>
                      <ImageIcon class="w-8 h-8 text-gray-400" />
                    </template>
                  </div>

                  <!-- 📋 카피라이트 -->
                  <div
                    v-if="imageCaptions[i]?.title && imageCaptions[i]?.description"
                    class="text-xs text-gray-700"
                  >
                    <div class="font-semibold text-gray-900 flex justify-between items-start">
                      <span>{{ imageCaptions[i].title }}</span>
                      <button
                        class="text-[11px] text-indigo-500 hover:text-indigo-700"
                        @click.stop="copyCaption(`${imageCaptions[i].title}\n${imageCaptions[i].description}`)"
                      >
                        복사
                      </button>
                    </div>
                    <div class="text-gray-600 mt-1">
                      {{ imageCaptions[i].description }}
                    </div>
                  </div>

                  <div
                    v-else-if="isCopyLoading"
                    class="flex items-center justify-center py-3 text-sm text-gray-400"
                  >
                    <div class="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin mr-2"></div>
                    카피라이트 생성 중...
                  </div>

                  <div v-else class="text-xs text-gray-400 italic text-center">
                    아직 카피라이트가 없습니다.
                  </div>
                </div>
              </div>
            </div>

            <!-- 🎬 영상 섹션 -->
            <div class="border-t pt-5">
              <div class="flex items-center gap-2 text-sm font-medium mb-2">
                <PlayCircle class="w-4 h-4 text-purple-600" />
                <span>생성된 영상</span>
              </div>

              <!-- 🔄 로딩 중일 때 -->
              <div v-if=" isVideoGenerating" class="space-y-2">
                <div class="text-sm text-gray-600">{{ videoStatus || "영상 생성 중..." }}</div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                  <div
                    class="bg-purple-600 h-3 rounded-full transition-all duration-300"
                    :style="{ width: `${videoProgress}%` }"
                  ></div>
                </div>
              </div>

              <!-- 🎥 영상 있을 때 -->
              <div
                v-else-if="videos.length"
                class="aspect-video bg-black rounded-lg overflow-hidden cursor-pointer"
                @click="openVideoModal"
              >
                <video
                  :src="videos[0]"
                  controls
                  autoplay
                  loop
                  class="w-full h-full object-cover"
                ></video>
              </div>

              <!-- 🕓 아직 영상이 없을 때 (플레이스홀더) -->
              <!-- <div
                v-else
                class="aspect-video bg-gray-50 border border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center text-gray-400 py-6"
              >
                <PlayCircle class="w-10 h-10 mb-2 text-gray-400" />
                <span class="text-sm">아직 생성된 영상이 없습니다.</span>
              </div> -->
              <div v-else></div>
            </div>

          </CardContent>

          <div class="p-6 border-t border-gray-100 mt-auto">
            <Button
              class="w-full bg-green-600 hover:bg-green-700 text-white py-6 text-base font-medium"
              :disabled="!images.length"
              @click="downloadAllImages"
            >
              <Download class="w-5 h-5 mr-2" />
              모든 파일 다운로드
            </Button>
          </div>
        </Card>



      </div>
    </main>

    <!-- 이미지 모달 -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="closeModal"
    >
      <div class="relative max-w-3xl w-full mx-4">
        <img :src="images[currentImage]" class="w-full rounded-lg object-contain max-h-[80vh]" />
        <button class="absolute top-4 right-4 bg-black/50 text-white rounded-full p-2" @click="closeModal">✕</button>
        <button class="absolute left-3 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full p-2" @click.stop="prevImage">‹</button>
        <button class="absolute right-3 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full p-2" @click.stop="nextImage">›</button>
      </div>
    </div>

    <!-- 영상 모달 -->
    <div
      v-if="showVideoModal"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="closeVideoModal"
    >
      <div class="relative max-w-4xl w-full mx-4">
        <video :src="videos[0]" controls autoplay class="w-full rounded-lg max-h-[80vh]"></video>
        <button class="absolute top-4 right-4 bg-black/50 text-white rounded-full p-2" @click="closeVideoModal">✕</button>
      </div>
    </div>
  </div>
</template>
