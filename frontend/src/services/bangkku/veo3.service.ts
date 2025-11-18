/**
 * Veo3 Video Generation Service
 * WebSocket을 통한 비디오 생성 서비스
 */

export interface VideoGenerationRequest {
  prompt: string;
  image: string;  // base64 data URL
  lastFrame?: string;  // base64 data URL
}

export interface VideoGenerationResult {
  video_url: string;
  thumbnail_url: string;
  duration: number;
  metadata: Record<string, any>;
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
    // WebSocket URL 설정
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // const host = import.meta.env.VITE_API_URL || 'localhost:12346';
    const websocket_host = import.meta.env.VITE_WEBSOCKET_URL || 'localhost:12346';
    this.wsUrl = `${protocol}//${websocket_host}/api/bangkku/ws/generate-video`;
    // this.wsUrl = `wss://${host}/api/bangkku/ws/generate-video`;
  }

  /**
   * 비디오 생성
   */
  async generateVideo(
    request: VideoGenerationRequest,
    callbacks: VideoGenerationCallbacks
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // WebSocket 연결
        this.ws = new WebSocket(this.wsUrl);

        // 연결 성공
        this.ws.onopen = () => {
          console.log('Veo3 WebSocket connected');

          // 요청 전송
          this.ws?.send(JSON.stringify({
            type: 'generate',
            prompt: request.prompt,
            image: request.image,
            lastFrame: request.lastFrame
          }));
        };

        // 메시지 수신
        this.ws.onmessage = (event) => {
          const data = JSON.parse(event.data);

          switch (data.type) {
            case 'progress':
              // 진행률 업데이트
              callbacks.onProgress?.(data.percent, data.message);
              break;

            case 'completed':
              // 완료
              callbacks.onCompleted?.(data.result);
              this.closeConnection();
              resolve();
              break;

            case 'error':
              // 에러
              callbacks.onError?.(data.error);
              this.closeConnection();
              reject(new Error(data.error));
              break;
          }
        };

        // 에러 핸들링
        this.ws.onerror = (error) => {
          console.error('Veo3 WebSocket error:', error);
          const errorMessage = 'WebSocket 연결 오류가 발생했습니다';
          callbacks.onError?.(errorMessage);
          this.closeConnection();
          reject(new Error(errorMessage));
        };

        // 연결 종료
        this.ws.onclose = () => {
          console.log('Veo3 WebSocket disconnected');
          this.ws = null;
        };

      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
        callbacks.onError?.(errorMessage);
        reject(error);
      }
    });
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

// 싱글톤 인스턴스
export const veo3Service = new Veo3Service();
