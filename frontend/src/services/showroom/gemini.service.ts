import { GoogleGenAI } from "@google/genai"

const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY

// -----------------------------
// 🧩 인터페이스 정의
// -----------------------------
export interface ShowroomOptions {
  prompt?: string
  brand?: string
  description?: string
  background?: string
  place?: string
  time?: string
  season?: string
  weather?: string
  usage?: string
  music?: string
  story?: string
  modelInfo?: any
  productImages?: string[]
  referenceImages?: string[]
}

export interface ShowroomResponse {
  images: string[]
  videos: string[]
}

// -----------------------------
// 🧠 Gemini 이미지 생성 (각도별 시점 포함)
// -----------------------------
export const processShowroomGenerationWithGemini = async (
  data: ShowroomOptions
): Promise<ShowroomResponse> => {
  if (!GEMINI_API_KEY) throw new Error("Gemini API key not found.")
  const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY })

  const {
    brand,
    description,
    background,
    place,
    time,
    season,
    weather,
    usage,
    music,
    story,
    modelInfo = [],
    productImages = [],
    referenceImages = [],
  } = data

  const images: string[] = []

  // ✅ 4가지 각도 정의
  const cameraAngles = [
    {
      label: "정면 구도 (Front View)",
      desc: "제품 중심의 기본 구도로, 브랜드와 피사체의 존재감을 강조",
    },
    {
      label: "측면 구도 (Side View)",
      desc: "제품의 형태와 깊이감을 보여주는 시점으로, 입체감과 실재감을 표현",
    },
    {
      label: "광각 구도 (Wide View)",
      desc: "공간 전체를 포착하며, 장면 분위기와 스토리를 강조하는 시점",
    },
    {
      label: "후면 구도 (Rear View)",
      desc: "모델 또는 제품을 뒤에서 포착하여 감성적이고 여운 있는 장면을 연출",
    },
  ]

  const hasModel =
    Array.isArray(modelInfo) &&
    modelInfo.length > 0 &&
    modelInfo.some((m: any) => m.gender)

  for (let i = 0; i < cameraAngles.length; i++) {
    const { label, desc } = cameraAngles[i]

    const fullPrompt = `
당신은 세계적인 광고 아트 디렉터입니다.
다음 정보를 바탕으로 ${brand || "브랜드"}의 ${label} 시점 이미지를 생성하세요.

📦 제품 설명:
${description || "제품 설명 없음"}

🎬 연출 정보:
- 장소: ${place || "실내 공간"}
- 배경: ${background || "미니멀하고 따뜻한 조명 아래"}
- 시간: ${time || "낮 또는 저녁"}
- 계절: ${season || "사계절 공통"}
- 날씨: ${weather || "맑음"}
- 사용 목적: ${usage || "브랜드 홍보용 이미지"}
- 음악/분위기: ${music || "감성적이고 따뜻한 분위기"}
- 스토리: ${story || "제품이 중심인 감성적인 장면"}

👥 인물 구성:
${
  hasModel
    ? modelInfo
        .slice(0, 3)
        .map(
          (m: any, idx: number) =>
            `모델 ${idx + 1}: ${m.gender || "성별 미정"}, ${
              m.age || "나이 미정"
            }, 복장: ${
              m.clothing === "custom"
                ? m.clothingCustom
                : m.clothing || "기본 복장"
            }, 관계: ${m.relation || "주인공"}`
        )
        .join("\n")
    : "모델 없음 — 제품 중심 구도 유지"
}

📸 카메라 연출:
- ${label}: ${desc}
- ${hasModel ? "인물과 제품이 조화된 구도" : "제품만 중심으로 구성"}
- 현실적 조명, 깊이감(Depth of Field) 표현
- 부드러운 시네마틱 톤, 자연스러운 명암 대비
- 텍스트, 로고, 워터마크 금지
- 모델(인물)은 아주 세련되고 아름답고 예쁘거나 잘생긴 동양인이고, 반드시 아시아 대한민국의 한국인이어야 한다.
`

    const inlineParts =
      [...productImages, ...referenceImages].slice(0, 3).map((img) => ({
        inlineData: {
          data: img.replace(/^data:image\/\w+;base64,/, ""),
          mimeType: "image/jpeg",
        },
      })) ?? []

    try {
      console.log(`🎬 [${label}] 이미지 생성 시작...`)

      const res = await ai.models.generateContent({
        model: "gemini-2.5-flash-image",
        contents: [
          {
            role: "user",
            parts: [
              {
                text: `아래 프롬프트를 참고하여 ${label} 시점의 시네마틱 광고 이미지를 생성하세요.`,
              },
              ...inlineParts,
              { text: fullPrompt },
            ],
          },
        ],
      })

      const parts = res.candidates?.[0]?.content?.parts || []
      const imageParts = parts.filter((p: any) => p.inlineData)

      if (imageParts.length > 0) {
        const base64 = imageParts[0].inlineData.data
        const mime = imageParts[0].inlineData.mimeType || "image/png"
        const dataUrl = `data:${mime};base64,${base64}`
        images[i] = dataUrl
        console.log(`✅ [${label}] 생성 완료`)
      } else {
        console.warn(`⚠️ [${label}] 응답에 이미지 데이터 없음`)
      }
    } catch (error) {
      console.error(`❌ [${label}] 이미지 생성 오류:`, error)
    }
  }

  if (images.length === 0) throw new Error("No images generated from Gemini.")
  return { images, videos: [] }
}

// -----------------------------
// ✨ 카피라이트 생성
// -----------------------------
export const generateCopywritingForShowroom = async ({
  prompt,
  imageAngle,
  brand,
}: {
  prompt: string
  imageAngle?: string
  brand?: string
}): Promise<{ title: string; description: string }> => {
  if (!GEMINI_API_KEY) throw new Error("Gemini API key not found.")
  const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY })

  const fullPrompt = `
당신은 ${brand || "프리미엄 브랜드"}의 카피라이터입니다.
다음 이미지는 ${imageAngle || "제품 장면"}을 표현합니다.

🧠 작성 규칙:
- 제목: 이미지 분위기를 표현하는 짧은 한 줄
- 설명: 제품 감성을 표현하는 한 문장
- 브랜드 감성: Aesop, Apple, Dior 스타일

제품 설명:
${prompt}
`

  try {
    const res = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: [{ role: "user", parts: [{ text: fullPrompt }] }],
    })

    const raw = res.candidates?.[0]?.content?.parts?.[0]?.text || ""
    const clean = raw.replace(/\*/g, "").trim()
    const title =
      clean.match(/제목\s*:\s*(.*)/)?.[1]?.trim() ||
      clean.split("\n")[0]?.trim() ||
      "감성적인 장면"
    const desc =
      clean.match(/설명\s*:\s*(.*)/)?.[1]?.trim() ||
      clean.split("\n")[1]?.trim() ||
      "제품의 분위기를 감성적으로 담은 장면입니다."
    return { title, description: desc }
  } catch (err) {
    console.error("❌ 카피라이트 생성 실패:", err)
    return {
      title: "카피 생성 실패",
      description: "AI 카피 생성 중 오류가 발생했습니다.",
    }
  }
}
