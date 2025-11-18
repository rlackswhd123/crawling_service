"""
Veo3 Video Generation Service
Google Veo 3.1을 사용한 비디오 생성 서비스
"""
import os
import base64
import asyncio
import logging
import re
from typing import Optional, Callable
from google import genai
from google.genai import types
from utils.timer import Timer


logger = logging.getLogger(__name__)


class Veo3Service:
    """Veo3 비디오 생성 서비스"""

    def __init__(self):
        """서비스 초기화"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        self.client = genai.Client(api_key=api_key)
        self.model = "veo-3.1-generate-preview"

    def base64_to_image(self, base64_string: str):
        """
        Base64 문자열을 Google GenAI SDK용 types.Blob Image로 안전하게 변환
        - data:image 헤더 제거
        - MIME 타입 자동 감지
        - padding 보정 처리
        """

        try:
            # 1️⃣ 헤더 제거
            # 예: data:image/png;base64,XXXXXX
            mime_type = "image/png"  # 기본값
            if base64_string.startswith("data:image"):
                match = re.match(r"data:(image/\w+);base64,(.*)", base64_string)
                if match:
                    mime_type, base64_string = match.groups()
                else:
                    base64_string = base64_string.split(",")[-1]

            # 2️⃣ 공백, 줄바꿈 완전 제거
            base64_string = re.sub(r"\s+", "", base64_string)

            # 3️⃣ padding 보정 (길이가 4의 배수여야 함)
            pad_len = len(base64_string) % 4
            if pad_len:
                base64_string += "=" * (4 - pad_len)

            # 4️⃣ Base64 → bytes
            image_bytes = base64.b64decode(base64_string)

            # 5️⃣ Blob 변환 (Google GenAI SDK 호환)
            blob = types.Blob(data=image_bytes, mime_type=mime_type)
            image = blob.as_image()

            # ✅ 로그용
            logger.info(f"[base64_to_image] MIME: {mime_type}, bytes: {len(image_bytes)}")
            return image

        except Exception as e:
            logger.error(f"[base64_to_image] 변환 실패: {str(e)}")
            raise



    # async def generate_video(
    #     self,
    #     prompt: str,
    #     image: Optional[str] = None,
    #     last_frame: Optional[str] = None,
    #     progress_callback: Optional[Callable[[int, str], None]] = None
    # ) -> dict:
    #     """
    #     비디오 생성

    #     Args:
    #         prompt: 비디오 생성 프롬프트
    #         image: 첫 프레임 이미지 (base64)
    #         last_frame: 마지막 프레임 이미지 (base64, optional)
    #         progress_callback: 진행률 콜백 함수 (percent, message)

    #     Returns:
    #         {
    #             "video_url": "data:video/mp4;base64,...",
    #             "thumbnail_url": "data:image/png;base64,...",
    #             "duration": 10.0,
    #             "metadata": {...}
    #         }
    #     """
    #     timer = Timer()
    #     timer.start()

    #     try:
    #         # 진행률 업데이트
    #         if progress_callback:
    #             await progress_callback(5, "이미지 변환 중...")

    #         # Base64 → PIL Image 변환 (types.Blob 사용)
    #         first_image = self.base64_to_image(image) if image else None
    #         if first_image:
    #             logger.info(f"Created first frame Image from Blob: {type(first_image)}")

    #         last_image = self.base64_to_image(last_frame) if last_frame else None
    #         if last_image:
    #             logger.info(f"Created last frame Image from Blob: {type(last_image)}")

    #         if not first_image:
    #             raise ValueError("First image is required for video generation")

    #         if progress_callback:
    #             await progress_callback(15, "비디오 생성 요청 중...")

    #         logger.info(f"Veo3 video generation started: {prompt[:50]}...")
    #         logger.info(f"Prompt length: {len(prompt)} chars")

    #         # 비디오 생성 시작 (last_frame은 config 안에)
    #         if last_image:
    #             logger.info("Using last frame for interpolation")
    #             operation = self.client.models.generate_videos(
    #                 model=self.model,
    #                 prompt=prompt,
    #                 image=first_image,
    #                 config=types.GenerateVideosConfig(
    #                     last_frame=last_image
    #                 )
    #             )
    #         else:
    #             operation = self.client.models.generate_videos(
    #                 model=self.model,
    #                 prompt=prompt,
    #                 image=first_image
    #             )

    #         logger.info(f"Video generation operation started: {operation.name}")

    #         # 10초마다 폴링
    #         poll_count = 0
    #         max_polls = 60  # 최대 10분

    #         while not operation.done and poll_count < max_polls:
    #             poll_count += 1

    #             # 진행률 계산 (15% ~ 90%)
    #             percent = min(15 + (poll_count * 75 // max_polls), 90)

    #             if progress_callback:
    #                 await progress_callback(
    #                     percent,
    #                     f"비디오 생성 중... {percent}% ({poll_count}/{max_polls} polls)"
    #                 )

    #             logger.info(f"Polling video generation: {percent}% ({poll_count}/{max_polls})")

    #             # 10초 대기
    #             await asyncio.sleep(10)

    #             # 상태 갱신
    #             operation = self.client.operations.get(operation)

    #         if not operation.done:
    #             raise TimeoutError("Video generation timeout - exceeded maximum polling time")

    #         if progress_callback:
    #             await progress_callback(95, "비디오 처리 중...")

    #         # 결과 확인
    #         if not operation.response or not operation.response.generated_videos:
    #             raise ValueError("No video generated in response")

    #         # 결과 가져오기
    #         video = operation.response.generated_videos[0]
    #         logger.info("Video generation completed successfully")

    #         # 비디오 base64 인코딩
    #         if hasattr(video.video, 'bytes_base64_encoded'):
    #             video_base64 = video.video.bytes_base64_encoded
    #             logger.info("Retrieved video as base64 (new SDK format)")
    #         elif hasattr(video.video, 'video_bytes'):
    #             # Old SDK format: raw bytes
    #             self.client.files.download(file=video.video)
    #             video_bytes = video.video.video_bytes
    #             video_base64 = base64.b64encode(video_bytes).decode('utf-8')
    #             logger.info("Retrieved and encoded video bytes (old SDK format)")
    #         else:
    #             # Try downloading and accessing bytes
    #             self.client.files.download(file=video.video)
    #             video_bytes = video.video.video_bytes
    #             video_base64 = base64.b64encode(video_bytes).decode('utf-8')
    #             logger.info("Downloaded and encoded video bytes")

    #         video_data_url = f"data:video/mp4;base64,{video_base64}"
    #         logger.info(f"Video ready for transmission: {len(video_base64)} base64 chars")

    #         # 썸네일은 첫 프레임 이미지 사용
    #         thumbnail_url = image

    #         # 실제 생성 시간
    #         generation_time = timer.stop()

    #         # 메타데이터
    #         metadata = {
    #             "model": self.model,
    #             "prompt": prompt,
    #             "generation_time": generation_time,
    #             "poll_count": poll_count,
    #             "has_last_frame": last_frame is not None
    #         }

    #         logger.info(f"Veo3 video generation completed in {generation_time:.2f}s")

    #         if progress_callback:
    #             await progress_callback(100, "완료!")

    #         return {
    #             "video_url": video_data_url,
    #             "thumbnail_url": thumbnail_url,
    #             "duration": 10.0,  # Veo3 기본 duration
    #             "metadata": metadata
    #         }

    #     except Exception as e:
    #         logger.error(f"Veo3 video generation failed: {str(e)}")
    #         raise

    async def generate_video(
            self,
            prompt: str,
            image: Optional[str] = None,
            last_frame: Optional[str] = None,
            progress_callback: Optional[Callable[[int, str], None]] = None
        ) -> dict:
            """
            Veo3 비디오 생성 (디버깅 강화 버전)
            """
            timer = Timer()
            timer.start()

            try:
                logger.info("=" * 80)
                logger.info("🎬 [Veo3] generate_video() invoked")
                logger.info(f"Prompt preview: {prompt[:200].replace(chr(10), ' ')}")
                logger.info(f"Image received? {'✅ yes' if image else '❌ no'}")
                logger.info(f"Last frame received? {'✅ yes' if last_frame else '❌ no'}")

                # 진행률 업데이트
                if progress_callback:
                    await progress_callback(5, "이미지 변환 중...")

                # Base64 → Blob 변환
                try:
                    first_image = self.base64_to_image(image) if image else None
                    if first_image:
                        logger.info(f"✅ First frame image converted to blob ({type(first_image)})")
                    else:
                        logger.error("❌ Image conversion failed — first_image is None")
                except Exception as e:
                    logger.exception(f"⚠️ Image conversion exception: {str(e)}")
                    raise ValueError("Image conversion failed")

                # 마지막 프레임
                last_image = None
                if last_frame:
                    try:
                        last_image = self.base64_to_image(last_frame)
                        logger.info(f"✅ Last frame converted successfully ({type(last_image)})")
                    except Exception as e:
                        logger.warning(f"⚠️ Last frame conversion failed: {e}")

                if not first_image:
                    raise ValueError("First image is required for video generation")

                if progress_callback:
                    await progress_callback(15, "비디오 생성 요청 중...")

                logger.info(f"🧠 Model: {self.model}")
                logger.info(f"Prompt length: {len(prompt)} chars")

                # 모델 호출
                try:
                    if last_image:
                        logger.info("⛓ Using last frame for interpolation (GenerateVideosConfig)")
                        operation = self.client.models.generate_videos(
                            model=self.model,
                            prompt=prompt,
                            image=first_image,
                            config=types.GenerateVideosConfig(last_frame=last_image)
                        )
                    else:
                        logger.info("🚀 Calling client.models.generate_videos() (no last frame)")
                        operation = self.client.models.generate_videos(
                            model=self.model,
                            prompt=prompt,
                            image=first_image
                        )

                    logger.info(f"✅ Operation started: {operation.name}")
                except Exception as e:
                    logger.exception(f"❌ generate_videos() call failed: {str(e)}")
                    raise

                # 폴링 (10초 간격)
                poll_count = 0
                max_polls = 60
                logger.info("⏳ Polling operation status...")
                while not operation.done and poll_count < max_polls:
                    poll_count += 1
                    percent = min(15 + (poll_count * 75 // max_polls), 90)
                    if progress_callback:
                        await progress_callback(percent, f"비디오 생성 중... ({percent}%)")

                    logger.info(f"🌀 Poll {poll_count}/{max_polls} - done={operation.done}")
                    await asyncio.sleep(10)

                    try:
                        operation = self.client.operations.get(operation)
                    except Exception as e:
                        logger.warning(f"⚠️ Operation polling error: {str(e)}")
                        continue

                if not operation.done:
                    logger.error("⏰ Timeout: Video generation took too long")
                    raise TimeoutError("Video generation timeout - exceeded maximum polling time")

                logger.info("✅ Operation completed, fetching response...")

                # 응답 점검
                if not operation.response:
                    logger.error("❌ operation.response is None or empty")
                    logger.debug(f"🔍 Full operation dump: {operation}")
                    raise ValueError("No operation.response returned from model")

                # generated_videos 유무 확인
                generated = getattr(operation.response, "generated_videos", None)
                if not generated:
                    logger.error("❌ operation.response.generated_videos is EMPTY or None")
                    logger.debug(f"🔍 operation.response structure: {operation.response}")
                    raise ValueError("No video generated in response")

                logger.info(f"✅ {len(generated)} video(s) generated")

                # 결과 추출
                video = generated[0]
                if hasattr(video.video, "bytes_base64_encoded"):
                    video_base64 = video.video.bytes_base64_encoded
                    logger.info("🎞 Retrieved video as base64 (new SDK format)")
                elif hasattr(video.video, "video_bytes"):
                    logger.info("📦 Downloading raw video bytes (old SDK format)")
                    self.client.files.download(file=video.video)
                    video_bytes = video.video.video_bytes
                    video_base64 = base64.b64encode(video_bytes).decode("utf-8")
                else:
                    logger.warning("⚠️ Unknown video format — attempting manual download")
                    self.client.files.download(file=video.video)
                    video_bytes = video.video.video_bytes
                    video_base64 = base64.b64encode(video_bytes).decode("utf-8")

                video_data_url = f"data:video/mp4;base64,{video_base64}"
                logger.info(f"📤 Video ready for return ({len(video_base64)} chars)")

                # 썸네일 및 메타데이터
                thumbnail_url = image
                total_time = timer.stop()

                metadata = {
                    "model": self.model,
                    "prompt": prompt[:200],
                    "generation_time": total_time,
                    "poll_count": poll_count,
                    "has_last_frame": last_frame is not None
                }

                logger.info(f"🎉 Veo3 video generation completed in {total_time:.2f}s")
                logger.info("=" * 80)

                if progress_callback:
                    await progress_callback(100, "완료!")

                return {
                    "video_url": video_data_url,
                    "thumbnail_url": thumbnail_url,
                    "duration": 10.0,
                    "metadata": metadata
                }

            except Exception as e:
                logger.exception(f"💥 Veo3 video generation failed: {str(e)}")
                raise


    async def generate_showroom_video(
        self,
        prompt: str,
        image: str,
        
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> dict:
        """
        🎬 쇼룸용 단일 이미지 기반 비디오 생성
        첫 번째 이미지를 기반으로 generate_video() 호출
        """
        try:
            if not image:
                raise ValueError("At least one image is required for showroom video generation")

            logger.info(f"[Showroom] Single image head: {image[:60]}...")
            logger.info("[Showroom] Forwarding to base video generator")        

            # ✅ 기존 generate_video 재사용
            result = await self.generate_video(
                prompt=prompt,
                image=image,
                last_frame=None,
                progress_callback=progress_callback
            )

            return result

        except Exception as e:
            logger.error(f"[Showroom] Veo3 showroom video generation failed: {str(e)}")
            raise




# 싱글톤 인스턴스
veo3_service = Veo3Service()

