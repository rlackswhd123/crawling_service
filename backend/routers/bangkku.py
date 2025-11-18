"""
Bangkku Router
방꾸 서비스 API 엔드포인트
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.bangkku import gemini_service
from services.bangkku.veo3_service import veo3_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ==================== Request Models ====================

class ImageProcessRequest(BaseModel):
    """단일 이미지 처리 요청"""
    prompt: str
    image: str  # base64 data URL

class MultipleImagesRequest(BaseModel):
    """다중 이미지 처리 요청"""
    prompt: str
    images: List[str]  # base64 data URLs

class VideoGenerationRequest(BaseModel):
    """비디오 생성 요청 (HTTP용)"""
    prompt: str
    image: str  # base64 data URL
    lastFrame: Optional[str] = None  # base64 data URL

class RemoveBackgroundRequest(BaseModel):
    """배경 제거 요청"""
    image: str  # base64 data URL

# ==================== Response Models ====================

class ProcessImageResponse(BaseModel):
    """이미지 처리 응답"""
    status: str
    result: str  # base64 data URL

class VideoGenerationResponse(BaseModel):
    """비디오 생성 응답"""
    status: str
    video_url: str
    thumbnail_url: str
    duration: float
    metadata: dict

# ==================== HTTP Endpoints ====================

@router.post("/process-image", response_model=ProcessImageResponse)
async def process_image(request: ImageProcessRequest):
    """
    단일 이미지 처리
    - 가구 제거
    - 가구 정면 샷 변환
    """
    try:
        result = await gemini_service.process_single_image(
            prompt=request.prompt,
            image=request.image
        )

        return ProcessImageResponse(
            status="success",
            result=result
        )

    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-multiple-images", response_model=ProcessImageResponse)
async def process_multiple_images(request: MultipleImagesRequest):
    """
    다중 이미지 처리
    - 3D 룸 생성
    """
    try:
        result = await gemini_service.process_multiple_images(
            prompt=request.prompt,
            images=request.images
        )

        return ProcessImageResponse(
            status="success",
            result=result
        )

    except Exception as e:
        logger.error(f"Multiple images processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remove-background", response_model=ProcessImageResponse)
async def remove_background(request: RemoveBackgroundRequest):
    """
    이미지 배경 제거 및 여백 크롭
    - AI 기반 배경 제거 (rembg)
    - 여백 자동 크롭
    """
    try:
        # Base64 → PIL Image
        pil_image = gemini_service.base64_to_pil(request.image)

        # 1단계: 배경 제거
        transparent_image = gemini_service.remove_background(pil_image)

        # 2단계: 여백 크롭
        cropped_image = gemini_service.crop_to_object(
            transparent_image,
            difference_threshold=5,
            padding_ratio=0.0
        )

        # 3단계: Base64로 변환 (PNG로 투명 배경 유지)
        result = gemini_service.pil_to_base64(cropped_image, format="PNG")

        return ProcessImageResponse(
            status="success",
            result=result
        )

    except Exception as e:
        logger.error(f"Background removal failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WebSocket Endpoint ====================

@router.websocket("/ws/generate-video")
async def generate_video_ws(websocket: WebSocket):
    """
    비디오 생성 WebSocket
    실시간 진행률 업데이트 제공
    """
    await websocket.accept()

    try:
        # 클라이언트로부터 요청 받기
        data = await websocket.receive_json()

        prompt = data.get("prompt")
        image = data.get("image")
        last_frame = data.get("lastFrame")

        if not prompt or not image:
            await websocket.send_json({
                "type": "error",
                "error": "prompt and image are required"
            })
            await websocket.close()
            return

        logger.info(f"Video generation started via WebSocket: {prompt[:50]}...")

        # 진행률 콜백
        async def progress_callback(percent: int, message: str):
            await websocket.send_json({
                "type": "progress",
                "percent": percent,
                "message": message
            })

        # 비디오 생성
        result = await veo3_service.generate_video(
            prompt=prompt,
            image=image,
            last_frame=last_frame,
            progress_callback=progress_callback
        )

        # 완료 메시지
        await websocket.send_json({
            "type": "completed",
            "result": result
        })

        logger.info("Video generation completed via WebSocket")

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })

    finally:
        await websocket.close()

# ==================== Health Check ====================

@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "bangkku",
        "endpoints": [
            "/process-image",
            "/process-multiple-images",
            "/remove-background",
            "/ws/generate-video"
        ]
    }


# ==================== WebSocket Endpoint (Showroom) ====================

@router.websocket("/showroom/ws/generate-video")
async def generate_showroom_video_ws(websocket: WebSocket):
    """
    쇼룸용 단일 이미지 기반 비디오 생성 WebSocket
    Gemini 결과 이미지를 받아 Veo3로 영상 합성
    """
    await websocket.accept()

    try:
        data = await websocket.receive_json()

        prompt = data.get("prompt")
        image = data.get("image")

        if not prompt or not image:
            await websocket.send_json({
                "type": "error",
                "error": "prompt and image are required"
            })
            await websocket.close()
            return

        logger.info("[Showroom] Video generation started (single image via generate_video)")

        # 진행률 콜백 (progress 이벤트 전송)
        async def progress_callback(percent: int, message: str):
            await websocket.send_json({
                "type": "progress",
                "percent": percent,
                "message": message
            })

        # ✅ 핵심 변경: generate_showroom_video → generate_video
        result = await veo3_service.generate_video(
            prompt=prompt,
            image=image,
            progress_callback=progress_callback
        )

        # 결과 전송
        await websocket.send_json({
            "type": "completed",
            "result": result
        })

        logger.info("[Showroom] Video generation completed successfully")

    except WebSocketDisconnect:
        logger.info("Showroom WebSocket disconnected")

    except Exception as e:
        logger.error(f"[Showroom] Video generation failed: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })

    finally:
        await websocket.close()
