/**
 * Bangkku Service Type Definitions
 * 방꾸 서비스의 타입 정의
 */

export interface ProcessedImage {
  id: string;
  originalFile: File;
  originalUrl: string;
  result: string | null;
  isProcessing: boolean;
  error: string | null;
}

export interface ImageUploadState {
  file: File;
  preview: string;
}

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

export interface VideoGenerationRequest {
  prompt: string;
  image: string;  // base64 data URL
  lastFrame?: string;  // optional base64 data URL
}

export interface VideoGenerationCallbacks {
  onProgress?: (message: string, percent: number) => void;
  onCompleted?: (videoUrl: string, thumbnailUrl: string, metadata: any) => void;
  onError?: (error: string) => void;
}

export type ImageKey = 'left' | 'front' | 'right' | 'background';

export interface Room3DImages {
  left: ImageUploadState | null;
  front: ImageUploadState | null;
  right: ImageUploadState | null;
  background: ImageUploadState | null;
}
