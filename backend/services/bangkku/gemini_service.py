"""
Gemini Image Processing Service
Google Gemini 2.5 Flash를 사용한 이미지 처리 서비스
"""
import os
import base64
import logging
import time
from typing import List, Optional, Dict, Any, Tuple
from io import BytesIO

import dotenv
from PIL import Image, ImageChops, ImageStat
import numpy as np
from google import genai
from google.genai.types import GenerateContentConfig, Part
from rembg import remove

from services.prompt_service import PromptService
from services.test_result_service import TestResultService

logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini 이미지 처리 서비스"""

    def __init__(self):
        """서비스 초기화"""

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash-preview-01-15"

        # Service layer instances
        self.prompt_service = PromptService()
        self.test_result_service = TestResultService()

    def base64_to_pil(self, base64_string: str) -> Image.Image:
        """Base64 문자열을 PIL Image로 변환"""
        # data:image/jpeg;base64, 부분 제거
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]

        image_bytes = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_bytes))

    def pil_to_base64(self, image: Image.Image, format: str = "PNG") -> str:
        """PIL Image를 Base64 문자열로 변환"""
        buffered = BytesIO()
        image.save(buffered, format=format)
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()
        return f"data:image/{format.lower()};base64,{img_base64}"

    def _estimate_background_color(self, image: Image.Image) -> Tuple[int, int, int]:
        """이미지 가장자리 색상을 샘플링하여 배경색을 추정합니다."""

        rgb_image = image.convert("RGB")
        width, height = rgb_image.size

        if width == 0 or height == 0:
            return (255, 255, 255)

        step_x = max(1, width // 50)
        step_y = max(1, height // 50)
        samples: List[Tuple[int, int, int]] = []

        for x in range(0, width, step_x):
            samples.append(rgb_image.getpixel((x, 0)))
            samples.append(rgb_image.getpixel((x, height - 1)))

        for y in range(0, height, step_y):
            samples.append(rgb_image.getpixel((0, y)))
            samples.append(rgb_image.getpixel((width - 1, y)))

        if not samples:
            stats = ImageStat.Stat(rgb_image)
            return tuple(int(channel) for channel in stats.mean[:3])

        sample_count = len(samples)
        avg = [sum(channel[i] for channel in samples) / sample_count for i in range(3)]
        return tuple(int(round(value)) for value in avg)

    def crop_to_object(
        self,
        image: Image.Image,
        difference_threshold: int = 8,
        padding_ratio: float = 0.01
    ) -> Image.Image:
        """
        배경 여백을 제거하고 가구 외곽선에 맞춰 이미지를 크롭합니다.

        Args:
            image: 크롭할 PIL 이미지
            difference_threshold: 배경색과의 최소 색상 차이(0-255)
            padding_ratio: 객체가 잘리지 않도록 bbox에 추가할 여유 비율

        Returns:
            여백이 제거된 이미지
        """

        if image is None:
            return image

        original_mode = image.mode
        working_image = image.copy()

        if working_image.mode not in ("RGBA", "LA"):
            working_image = working_image.convert("RGBA")

        alpha_channel = working_image.getchannel("A")
        bbox = alpha_channel.getbbox()

        if bbox and bbox != (0, 0, working_image.width, working_image.height):
            crop_source = working_image
        else:
            rgb_image = working_image.convert("RGB")
            background_color = self._estimate_background_color(rgb_image)
            rgb_array = np.asarray(rgb_image, dtype=np.int16)

            if rgb_array.ndim != 3 or rgb_array.shape[2] != 3:
                crop_source = working_image
                bbox = None
            else:
                background_vector = np.array(background_color, dtype=np.int16)
                channel_diff = np.abs(rgb_array - background_vector)
                max_diff = channel_diff.max(axis=2)

                # Adaptive thresholding: look at border noise to avoid full-frame crops
                border = max(1, min(working_image.width, working_image.height) // 20)
                border_mask = np.concatenate(
                    [
                        max_diff[:border, :].ravel(),
                        max_diff[-border:, :].ravel(),
                        max_diff[:, :border].ravel(),
                        max_diff[:, -border:].ravel(),
                    ]
                )

                if border_mask.size:
                    noise_floor = float(np.percentile(border_mask, 95))
                else:
                    noise_floor = 0.0

                adaptive_threshold = max(difference_threshold, noise_floor + 3.0)
                mask = max_diff > adaptive_threshold

                if not np.any(mask):
                    bbox = None
                    crop_source = working_image
                else:
                    ys = np.where(mask.any(axis=1))[0]
                    xs = np.where(mask.any(axis=0))[0]

                    top = int(ys[0])
                    bottom = int(ys[-1]) + 1
                    left_idx = int(xs[0])
                    right_idx = int(xs[-1]) + 1

                    bbox = (left_idx, top, right_idx, bottom)
                    crop_source = working_image

        if not bbox:
            return image

        left, upper, right, lower = bbox
        if padding_ratio > 0:
            width, height = crop_source.size
            pad_w = int((right - left) * padding_ratio)
            pad_h = int((lower - upper) * padding_ratio)
            left = max(0, left - pad_w)
            upper = max(0, upper - pad_h)
            right = min(width, right + pad_w)
            lower = min(height, lower + pad_h)

        cropped = crop_source.crop((left, upper, right, lower))

        if cropped.mode != original_mode:
            try:
                cropped = cropped.convert(original_mode)
            except ValueError:
                cropped = cropped.convert("RGB")

        return cropped

    def _format_from_mime(self, mime_type: Optional[str]) -> str:
        if not mime_type:
            return "PNG"

        try:
            format_name = mime_type.split("/")[-1].upper()
            if format_name == "JPG":
                format_name = "JPEG"
            return format_name
        except Exception:
            return "PNG"

    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        AI 기반 배경 제거 (rembg 사용)

        Args:
            image: 배경을 제거할 PIL 이미지

        Returns:
            투명 배경(RGBA)의 이미지
        """
        try:
            # rembg로 배경 제거 (자동으로 RGBA 반환)
            output = remove(image)
            logger.info("Background removed successfully using rembg")
            return output
        except Exception as e:
            logger.warning(f"Background removal failed: {str(e)}, returning original")
            # 실패시 원본을 RGBA로 변환해서 반환
            if image.mode != "RGBA":
                return image.convert("RGBA")
            return image

    async def process_single_image(
        self,
        prompt: str,
        image: str
    ) -> str:
        """
        단일 이미지 처리

        Args:
            prompt: 이미지 처리 프롬프트
            image: 이미지 (base64)

        Returns:
            처리된 이미지 (base64 data URL)
        """
        try:
            # Base64 → PIL Image 변환
            pil_image = self.base64_to_pil(image)

            logger.info(f"Gemini single image processing: {prompt[:50]}...")

            # Gemini API 호출
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=[
                    Part.from_text(prompt),
                    Part.from_image(pil_image)
                ],
                config=GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=8192
                )
            )

            # 생성된 이미지 추출
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]

                # 이미지 파트 찾기
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # 이미지 데이터를 base64로 변환
                        image_bytes = part.inline_data.data
                        # img_base64 = base64.b64encode(image_bytes).decode()
                        mime_type = part.inline_data.mime_type
                        # result_url = f"data:{mime_type};base64,{img_base64}"

                        # 이미지 처리: 배경 제거 → 여백 크롭
                        format_name = self._format_from_mime(mime_type)
                        generated_image = Image.open(BytesIO(image_bytes))

                        # 1단계: AI 배경 제거 (투명 배경으로)
                        transparent_image = self.remove_background(generated_image)

                        # 2단계: 여백 크롭 (알파 채널 기반으로 정확하게)
                        cropped_image = self.crop_to_object(
                            transparent_image,
                            difference_threshold=5,  # 더 민감하게
                            padding_ratio=0.0  # 여백 없이
                        )

                        # 3단계: 포맷에 맞게 변환
                        if format_name in {"JPEG", "JPG"}:
                            # JPEG는 투명도 지원 안함 → 흰 배경으로
                            if cropped_image.mode == "RGBA":
                                white_bg = Image.new("RGB", cropped_image.size, (255, 255, 255))
                                white_bg.paste(cropped_image, mask=cropped_image.split()[3])
                                cropped_image = white_bg

                        result_url = self.pil_to_base64(cropped_image, format=format_name)

                        logger.info("Gemini single image processing completed")
                        return result_url

            # 이미지가 없으면 원본 반환
            logger.warning("No image generated, returning original")
            return image

        except Exception as e:
            logger.error(f"Gemini single image processing failed: {str(e)}")
            raise

    async def process_multiple_images(
        self,
        prompt: str,
        images: List[str]
    ) -> str:
        """
        다중 이미지 처리

        Args:
            prompt: 이미지 처리 프롬프트
            images: 이미지 리스트 (base64)

        Returns:
            처리된 이미지 (base64 data URL)
        """
        try:
            logger.info(f"Gemini multiple images processing: {len(images)} images, {prompt[:50]}...")

            # Base64 → PIL Image 변환
            pil_images = [self.base64_to_pil(img) for img in images]

            # 컨텐츠 구성: 프롬프트 + 이미지들
            contents = [Part.from_text(prompt)]
            contents.extend([Part.from_image(img) for img in pil_images])

            # Gemini API 호출
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=8192
                )
            )

            # 생성된 이미지 추출
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]

                # 이미지 파트 찾기
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # 이미지 데이터를 base64로 변환
                        image_bytes = part.inline_data.data
                        # img_base64 = base64.b64encode(image_bytes).decode()
                        mime_type = part.inline_data.mime_type
                        # result_url = f"data:{mime_type};base64,{img_base64}"

                        # 이미지 처리: 배경 제거 → 여백 크롭
                        format_name = self._format_from_mime(mime_type)
                        generated_image = Image.open(BytesIO(image_bytes))

                        # 1단계: AI 배경 제거 (투명 배경으로)
                        transparent_image = self.remove_background(generated_image)

                        # 2단계: 여백 크롭 (알파 채널 기반으로 정확하게)
                        cropped_image = self.crop_to_object(
                            transparent_image,
                            difference_threshold=5,  # 더 민감하게
                            padding_ratio=0.0  # 여백 없이
                        )

                        # 3단계: 포맷에 맞게 변환
                        if format_name in {"JPEG", "JPG"}:
                            # JPEG는 투명도 지원 안함 → 흰 배경으로
                            if cropped_image.mode == "RGBA":
                                white_bg = Image.new("RGB", cropped_image.size, (255, 255, 255))
                                white_bg.paste(cropped_image, mask=cropped_image.split()[3])
                                cropped_image = white_bg

                        result_url = self.pil_to_base64(cropped_image, format=format_name)

                        logger.info("Gemini multiple images processing completed")
                        return result_url

            # 이미지가 없으면 첫 번째 이미지 반환
            logger.warning("No image generated, returning first image")
            return images[0]

        except Exception as e:
            logger.error(f"Gemini multiple images processing failed: {str(e)}")
            raise

    async def process_with_default_prompt(
        self,
        prompt_kind: str,
        image: str,
        input_params: Optional[Dict[str, Any]] = None,
        save_result: bool = True
    ) -> Dict[str, Any]:
        """
        기본 프롬프트를 사용한 이미지 처리 (DB 연동)
        Single responsibility: AI 처리 + 서비스 레이어 호출

        Args:
            prompt_kind: Service/feature path (e.g., 'bangkku/furniture_removal')
            image: Image (base64)
            input_params: Additional input parameters to save
            save_result: Whether to save test result to DB

        Returns:
            Dict: {
                'result': base64 image,
                'prompt_key': prompt ID used,
                'execution_time_ms': processing time,
                'test_result_key': saved result ID (if save_result=True)
            }
        """
        start_time = time.time()
        prompt_key = None
        success = False
        error_msg = None
        result_image = None

        try:
            # 1. Get default prompt from DB
            prompt_data = await self.prompt_service.get_default_prompt(prompt_kind)
            if not prompt_data:
                raise ValueError(f"No default prompt found for {prompt_kind}")

            prompt_key = prompt_data['prompt_key']
            prompt_text = prompt_data['prompt_text']

            # 2. Increment usage count
            await self.prompt_service.increment_usage(prompt_key)

            # 3. Process image with AI
            result_image = await self.process_single_image(prompt_text, image)

            # 4. Mark as success
            success = True
            await self.prompt_service.increment_success(prompt_key)

            execution_time_ms = int((time.time() - start_time) * 1000)

            # 5. Save test result if requested
            test_result_key = None
            if save_result and prompt_key:
                from database.models import TestResultCreate

                test_result_key = await self.test_result_service.create_test_result(
                    TestResultCreate(
                        prompt_key=prompt_key,
                        input_params=input_params or {},
                        output_url=result_image[:100] if result_image else None,  # Save first 100 chars
                        execution_time_ms=execution_time_ms,
                        token_cnt=None,  # Gemini doesn't provide token count easily
                        cost_amount=None,  # Would need pricing calculation
                        success_yn=1,
                        error_msg=None
                    )
                )

            return {
                'result': result_image,
                'prompt_key': prompt_key,
                'execution_time_ms': execution_time_ms,
                'test_result_key': test_result_key
            }

        except Exception as e:
            error_msg = str(e)
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Save failure result
            if save_result and prompt_key:
                from database.models import TestResultCreate

                await self.test_result_service.create_test_result(
                    TestResultCreate(
                        prompt_key=prompt_key,
                        input_params=input_params or {},
                        output_url=None,
                        execution_time_ms=execution_time_ms,
                        token_cnt=None,
                        cost_amount=None,
                        success_yn=0,
                        error_msg=error_msg
                    )
                )

            logger.error(f"Process with default prompt failed: {error_msg}")
            raise

    async def process_multiple_with_default_prompt(
        self,
        prompt_kind: str,
        images: List[str],
        input_params: Optional[Dict[str, Any]] = None,
        save_result: bool = True
    ) -> Dict[str, Any]:
        """
        기본 프롬프트를 사용한 다중 이미지 처리 (DB 연동)

        Args:
            prompt_kind: Service/feature path
            images: Images list (base64)
            input_params: Additional input parameters to save
            save_result: Whether to save test result to DB

        Returns:
            Dict: {
                'result': base64 image,
                'prompt_key': prompt ID used,
                'execution_time_ms': processing time,
                'test_result_key': saved result ID (if save_result=True)
            }
        """
        start_time = time.time()
        prompt_key = None
        error_msg = None
        result_image = None

        try:
            # 1. Get default prompt
            prompt_data = await self.prompt_service.get_default_prompt(prompt_kind)
            if not prompt_data:
                raise ValueError(f"No default prompt found for {prompt_kind}")

            prompt_key = prompt_data['prompt_key']
            prompt_text = prompt_data['prompt_text']

            # 2. Increment usage
            await self.prompt_service.increment_usage(prompt_key)

            # 3. Process images
            result_image = await self.process_multiple_images(prompt_text, images)

            # 4. Mark success
            await self.prompt_service.increment_success(prompt_key)

            execution_time_ms = int((time.time() - start_time) * 1000)

            # 5. Save test result
            test_result_key = None
            if save_result and prompt_key:
                from database.models import TestResultCreate

                test_result_key = await self.test_result_service.create_test_result(
                    TestResultCreate(
                        prompt_key=prompt_key,
                        input_params=input_params or {},
                        output_url=result_image[:100] if result_image else None,
                        execution_time_ms=execution_time_ms,
                        token_cnt=None,
                        cost_amount=None,
                        success_yn=1,
                        error_msg=None
                    )
                )

            return {
                'result': result_image,
                'prompt_key': prompt_key,
                'execution_time_ms': execution_time_ms,
                'test_result_key': test_result_key
            }

        except Exception as e:
            error_msg = str(e)
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Save failure result
            if save_result and prompt_key:
                from database.models import TestResultCreate

                await self.test_result_service.create_test_result(
                    TestResultCreate(
                        prompt_key=prompt_key,
                        input_params=input_params or {},
                        output_url=None,
                        execution_time_ms=execution_time_ms,
                        token_cnt=None,
                        cost_amount=None,
                        success_yn=0,
                        error_msg=error_msg
                    )
                )

            logger.error(f"Process multiple with default prompt failed: {error_msg}")
            raise

# 싱글톤 인스턴스
gemini_service = GeminiService()
