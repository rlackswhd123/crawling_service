/**
 * Veo3 Video Generation Service
 * WebSocket을 통한 영상 합성 서비스
 */

export interface VideoGenerationRequest {
  prompt: string;
  image: string; // base64 data URL
  lastFrame?: string; // base64 data URL
}

export interface ShowroomVideoRequest {
  brand: string;
  description: string;
  background?: string;
  place?: string;
  time?: string;
  season?: string;
  weather?: string;
  usage?: string;
  music?: string;
  story?: string;
  cameraPath?: string;
  imageRatio?: string;
  videoQuality?: string;
  directingNotes?: string;
  image: string; // base64 image 배열
}

export interface VideoGenerationResult {
  video_url: string;
  thumbnail_url?: string;
  duration?: number;
}

export interface VideoGenerationCallbacks {
  onProgress?: (percent: number, message: string) => void;
  onCompleted?: (result: VideoGenerationResult) => void;
  onError?: (error: string) => void;
}

export class Veo3Service {
  private ws: WebSocket | null = null;
  private readonly wsUrl: string;

  constructor() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const websocket_host = import.meta.env.VITE_WEBSOCKET_URL || "localhost:12345";
    this.wsUrl = `${protocol}//${websocket_host}/api/bangkku/ws/generate-video`;
  }

  /**
   * 🧠 공통 WebSocket 요청 처리
   */
  private async sendWebSocketRequest(
    wsUrl: string,
    body: Record<string, any>,
    callbacks: VideoGenerationCallbacks
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // 중복 연결 방지
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          console.warn("🔄 기존 WebSocket 세션 종료 중...");
          this.ws.close();
        }

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log("🎥 Veo3 WebSocket 연결됨");
          this.ws?.send(JSON.stringify(body));
        };

        this.ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          switch (data.type) {
            case "progress":
              callbacks.onProgress?.(data.percent, data.message);
              break;
            case "completed":
              callbacks.onCompleted?.(data.result);
              this.closeConnection();
              resolve();
              break;
            case "error":
              callbacks.onError?.(data.error);
              this.closeConnection();
              reject(new Error(data.error));
              break;
          }
        };

        this.ws.onerror = (error) => {
          console.error("❌ Veo3 WebSocket 오류:", error);
          const msg = "WebSocket 연결 중 오류가 발생했습니다.";
          callbacks.onError?.(msg);
          this.closeConnection();
          reject(new Error(msg));
        };

        this.ws.onclose = () => {
          console.log("🔌 Veo3 WebSocket 연결 종료");
          this.ws = null;
        };
      } catch (error) {
        const msg = error instanceof Error ? error.message : "알 수 없는 오류";
        callbacks.onError?.(msg);
        reject(error);
      }
    });
  }

  /**
   * ✅ 기본 단일 이미지 비디오 생성
   */
  async generateVideo(
    request: VideoGenerationRequest,
    callbacks: VideoGenerationCallbacks
  ): Promise<void> {
    return this.sendWebSocketRequest(
      this.wsUrl, // ✅ wsUrl 명시
      {
        type: "generate",
        prompt: request.prompt,
        image: request.image,
        lastFrame: request.lastFrame,
      },
      callbacks
    );
  }

  /**
 * 🚀 쇼룸용 영상 생성 (Gemini 결과 기반)
 */
async generateShowroomVideo(
    request: ShowroomVideoRequest,
    callbacks: VideoGenerationCallbacks
  ): Promise<void> {
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
      cameraPath,
      imageRatio,
      videoQuality,
      directingNotes,
      image,
    } = request;

    if (!image) {
      throw new Error("이미지 데이터가 없습니다.");
    }

    // ✅ (1) Base64 이미지 정규화: 헤더 제거 + padding 보정
    const cleanImage = (() => {
      let img = image.trim();

      // data:image 헤더 제거
      if (img.startsWith("data:image")) {
        const commaIndex = img.indexOf(",");
        if (commaIndex !== -1) img = img.slice(commaIndex + 1);
      }

      // padding 보정 (길이가 4의 배수가 되도록)
      const pad = img.length % 4;
      if (pad) img += "=".repeat(4 - pad);

      return img;
    })();

    // ✅ (2) 자연어 변환 매핑
    const cameraPathMap: Record<string, string> = {
      "pan-left": "카메라가 왼쪽으로 부드럽게 이동하며 장면을 따라간다.",
      "pan-right": "카메라가 오른쪽으로 부드럽게 이동하며 공간을 탐색한다.",
      "zoom-in": "카메라가 피사체 쪽으로 천천히 다가가며 초점을 맞춘다.",
      "zoom-out": "카메라가 뒤로 물러나며 전체 구도를 드러낸다.",
      "orbit": "카메라가 피사체를 중심으로 원형으로 회전한다.",
      "focus-shift": "카메라의 초점이 다른 피사체로 부드럽게 이동한다.",
      "fixed": "카메라는 고정된 시점에서 장면을 포착한다.",
    };

    const ratioMap: Record<string, string> = {
      "1:1": "정사각형 비율",
      "16:9": "와이드 비율 (풍경형)",
      "4:3": "표준 비율",
      "3:4": "세로형 비율",
      "9:16": "모바일 스토리형 세로 비율",
    };

    const qualityMap: Record<string, string> = {
      "720p": "HD (1280x720)",
      "1080p": "Full HD (1920x1080)",
      "4K": "4K Ultra HD (3840x2160)",
    };

    // ✅ (3) Veo 친화형 프롬프트 구성 — 모든 정보 포함, 명령문 제거
    const prompt = `
    시네마틱 제품 광고 장면.

    [시작시퀀스]
    ${brand}제품이며, 제품설명은 ${description || "제품"}이다.  
    ${background || "따뜻한 조명 아래의 미니멀한 공간"} 속에서  
    제품의 질감과 형태가 부드럽게 드러난다.  
    조명은 ${background?.includes("조명") ? background : "부드럽고 따뜻한 조명"}이며,  
    카메라는 천천히 제품 쪽으로 이동하며 초점을 맞춘다.

    [중간흐름]
    장면은 ${place || "실내 공간"}으로 확장되며,  
    ${season || "사계절"}의 ${time || "특정 시간"}대, ${weather || "맑은 날씨"} 분위기가 표현된다.  
    ${cameraPathMap[cameraPath] || "카메라는 자연스럽게 이동하며 제품 중심으로 장면을 탐색한다."}  
    전체 구도는 ${ratioMap[imageRatio] || "와이드 비율 (풍경형)"},  
    ${qualityMap[videoQuality] || "Full HD (1920x1080)"} 품질로 표현된다.  
    음악은 없으며, 조명은 현실적인 톤으로 유지된다.

    [마무리시퀀스]
    카메라는 제품을 중심으로 부드럽게 회전하며 마무리 장면을 만든다.  
    ${story || "제품이 중심이 되어 공간 전체가 따뜻한 분위기로 마무리된다."}  
    ${directingNotes || "부드러운 빛, 현실적인 반사, 섬세한 질감"}이 강조된다.  
    장면 전체는 사실적인 색감과 부드러운 대비로 마무리된다.

    ⚠️ 제약 조건:
    - 인물, 손, 불꽃, 연기, 향, 점화 등의 표현은 포함되지 않는다.  
    - 카메라는 부드럽게 이동하며, 급격한 회전이나 컷 전환은 없어야 한다.  
    - 텍스트, 로고, 워터마크는 포함되지 않는다.  
    - 영상은 사실적이며, 제품 중심으로 표현된다.
    `.trim();
      // .replace(/\s+/g, " ") 
    


  

    // ✅ (4) 요청 body
    const body = {
      type: "generate",
      prompt: prompt.trim(),
      // image: cleanImage,
      image: image.startsWith("data:image")
  ? image
  : `data:image/png;base64,${cleanImage}`,
    };

    console.log("🎬 Veo 요청 body", {
      prompt: prompt.substring(0, 200) + "...",
      imageHead: cleanImage.slice(0, 40) + "...",
    });

    // ✅ (5) WebSocket 연결 및 전송
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const websocket_host =
      import.meta.env.VITE_WEBSOCKET_URL || "localhost:12345";
    const showroomUrl = `${protocol}//${websocket_host}/api/bangkku/showroom/ws/generate-video`;

    return this.sendWebSocketRequest(showroomUrl, body, callbacks);
  }



  /**
   * 연결 종료
   */
  closeConnection(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.close();
    }
    this.ws = null;
  }

  /**
   * 연결 상태 확인
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// ✅ 싱글톤 인스턴스
export const veo3Service = new Veo3Service();

