import { GoogleGenAI } from '@google/genai';
import { getDefaultPrompt } from '@/services/common/prompt.service';
import type { Prompt } from '@/types/prompt.types';

const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

if (!GEMINI_API_KEY) {
  console.error('VITE_GEMINI_API_KEY is not set in .env file');
}

/**
 * Convert File to base64 string
 */
export const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

export interface GeminiImageProcessOptions {
  prompt: string;
  imageFile: File;
}

export interface GeminiMultipleImagesOptions {
  prompt: string;
  imageFiles: File[];
}

export interface GeminiResponse {
  editedUrl: string;
}

/**
 * Process single image with Gemini
 */
export const processImageWithGemini = async (
  options: GeminiImageProcessOptions
): Promise<GeminiResponse> => {
  const { prompt, imageFile } = options;

  if (!GEMINI_API_KEY) {
    throw new Error('Gemini API key is not configured');
  }

  try {
    const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });

    // Convert to base64 and split to remove data URL prefix
    const base64Data = await fileToBase64(imageFile);

    const imagePart = {
      inlineData: {
        data: base64Data.split(',')[1], // Remove "data:image/png;base64," prefix
        mimeType: imageFile.type
      }
    };

    console.log('Sending request to Gemini...');
    console.log('Prompt:', prompt.substring(0, 100) + '...');
    console.log('Image type:', imageFile.type);

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image-preview',
      contents: [imagePart, prompt] // Image first, then prompt
    });

    console.log('Gemini response received');

    // Extract generated image from response
    const parts = response.candidates?.[0]?.content?.parts || [];
    const generatedImage = parts.find(part => part.inlineData) || parts[0];

    if (generatedImage && 'inlineData' in generatedImage) {
      const base64Image = generatedImage.inlineData.data;
      const editedUrl = `data:${generatedImage.inlineData.mimeType};base64,${base64Image}`;
      return { editedUrl };
    }

    throw new Error('No image generated from Gemini response');
  } catch (error) {
    console.error('Gemini API error:', error);
    throw error;
  }
};

// ==================== Prompt Management Integration ====================

/**
 * 프롬프트 종류로 기본 프롬프트 가져오기
 */
export const getPromptByKind = async (promptKind: string): Promise<Prompt | null> => {
  try {
    return await getDefaultPrompt(promptKind);
  } catch (error) {
    console.error(`Failed to fetch prompt for ${promptKind}:`, error);
    return null;
  }
};

/**
 * 프롬프트 관리 시스템과 통합된 이미지 처리 (단일 이미지)
 * @param promptKind - 프롬프트 종류 (e.g., "bangkku/furniture-removal")
 * @param imageFile - 처리할 이미지 파일
 * @param customPrompt - (선택) 커스텀 프롬프트 (기본 프롬프트 대신 사용)
 */
export const processImageWithManagedPrompt = async (
  promptKind: string,
  imageFile: File,
  customPrompt?: string
): Promise<GeminiResponse> => {
  let promptText = customPrompt;

  // 커스텀 프롬프트가 없으면 DB에서 기본 프롬프트 가져오기
  if (!promptText) {
    const prompt = await getPromptByKind(promptKind);
    if (!prompt) {
      throw new Error(`No default prompt found for ${promptKind}`);
    }
    promptText = prompt.promptText;
    console.log(`Using managed prompt for ${promptKind} (ID: ${prompt.promptKey})`);
  }

  // 기존 processImageWithGemini 함수 호출
  return processImageWithGemini({
    prompt: promptText,
    imageFile,
  });
};

/**
 * 프롬프트 관리 시스템과 통합된 이미지 처리 (다중 이미지)
 * @param promptKind - 프롬프트 종류 (e.g., "bangkku/3d-room-generator")
 * @param imageFiles - 처리할 이미지 파일 배열
 * @param customPrompt - (선택) 커스텀 프롬프트 (기본 프롬프트 대신 사용)
 */
export const processMultipleImagesWithManagedPrompt = async (
  promptKind: string,
  imageFiles: File[],
  customPrompt?: string
): Promise<GeminiResponse> => {
  let promptText = customPrompt;

  // 커스텀 프롬프트가 없으면 DB에서 기본 프롬프트 가져오기
  if (!promptText) {
    const prompt = await getPromptByKind(promptKind);
    if (!prompt) {
      throw new Error(`No default prompt found for ${promptKind}`);
    }
    promptText = prompt.promptText;
    console.log(`Using managed prompt for ${promptKind} (ID: ${prompt.promptKey})`);
  }

  // 기존 processMultipleImagesWithGemini 함수 호출
  return processMultipleImagesWithGemini({
    prompt: promptText,
    imageFiles,
  });
};

/**
 * Process multiple images with Gemini
 */
export const processMultipleImagesWithGemini = async (
  options: GeminiMultipleImagesOptions
): Promise<GeminiResponse> => {
  const { prompt, imageFiles } = options;

  if (!GEMINI_API_KEY) {
    throw new Error('Gemini API key is not configured');
  }

  try {
    const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });

    // Convert all images to base64
    const imageParts = await Promise.all(
      imageFiles.map(async (file) => {
        const base64Data = await fileToBase64(file);
        return {
          inlineData: {
            data: base64Data.split(',')[1],
            mimeType: file.type
          }
        };
      })
    );

    console.log('Sending request to Gemini...');
    console.log('Prompt:', prompt.substring(0, 100) + '...');
    console.log('Number of images:', imageFiles.length);

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image-preview',
      contents: [...imageParts, prompt] // All images, then prompt
    });

    console.log('Gemini response received');

    // Extract generated image from response
    const parts = response.candidates?.[0]?.content?.parts || [];
    const generatedImage = parts.find(part => part.inlineData) || parts[0];

    if (generatedImage && 'inlineData' in generatedImage) {
      const base64Image = generatedImage.inlineData.data;
      const editedUrl = `data:${generatedImage.inlineData.mimeType};base64,${base64Image}`;
      return { editedUrl };
    }

    throw new Error('No image generated from Gemini response');
  } catch (error) {
    console.error('Gemini API error:', error);
    throw error;
  }
};

export const processMultipleImagesWithGeminiV2 = async (
  options: GeminiMultipleImagesOptions
): Promise<GeminiResponse> => {
  const { prompt, imageFiles } = options;

  if (!GEMINI_API_KEY) {
    throw new Error('Gemini API key is not configured');
  }

  try {
    const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });

    // ✅ 1️⃣ 이미지 Base64 변환
    const imageParts = await Promise.all(
      imageFiles.map(async (file) => {
        const base64 = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => {
            const result = (reader.result as string).split(',')[1];
            resolve(result);
          };
          reader.onerror = reject;
          reader.readAsDataURL(file);
        });

        return {
          inlineData: {
            data: base64,
            mimeType: file.type,
          },
        };
      })
    );

    // ✅ 2️⃣ 역할 명시 + 명확한 프롬프트 구조
//     const structuredPrompt = `
// 당신은 전문 이미지 합성가입니다.
// 첫 번째 이미지는 인물 사진입니다.
// 두 번째 이미지는 적용할 헤어스타일 이미지입니다.
// 두 번째 이미지의 머리카락을 첫 번째 인물의 머리에 자연스럽게 합성하세요.
// 조명과 피부 톤을 맞추고, 머리 경계를 부드럽게 처리하세요.
// 원본 이미지를 그대로 보여주지 말고, 완성된 합성 이미지만 생성하세요.
// 추가적인 텍스트나 설명 없이 완성된 이미지 하나만 반환하세요.
// `;

    // ✅ 3️⃣ 요청 구조 (각 이미지 앞에 역할 설명 추가)
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-image-preview",
      contents: [
        {
          role: "user",
          parts: [
            { text: "첫 번째 이미지는 인물 사진입니다." },
            imageParts[0],
            { text: "두 번째 이미지는 적용할 헤어스타일 이미지입니다." },
            imageParts[1],
            { text: prompt }, // 👈 명확한 지시
          ],
        },
      ],
    });

    console.log('Gemini response received ✅');

    // ✅ 4️⃣ 결과 이미지 추출
    const parts = response.candidates?.[0]?.content?.parts || [];
    const generatedImage = parts.find((p) => p.inlineData) || parts[0];

    if (generatedImage && 'inlineData' in generatedImage) {
      const base64Image = generatedImage.inlineData.data;
      const editedUrl = `data:${generatedImage.inlineData.mimeType};base64,${base64Image}`;
      return { editedUrl };
    }

    throw new Error('No image generated from Gemini response');
  } catch (error) {
    console.error('Gemini V2 multi-image error:', error);
    throw error;
  }
};

