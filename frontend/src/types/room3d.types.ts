/**
 * Room 3D Generation Types
 * 3D 룸 생성 관련 타입 정의
 */

export type RoomStructure = 'ㅡ자' | 'ㄱ자' | 'ㄷ자';

export type WallType = 'left' | 'front' | 'right';

export interface RoomStructureConfig {
  name: RoomStructure;
  label: string;
  wallCount: number;
  walls: WallType[];
  description: string;
}

/**
 * 방 구조별 설정
 */
export const ROOM_STRUCTURE_CONFIGS: RoomStructureConfig[] = [
  {
    name: 'ㅡ자',
    label: 'ㅡ자형 (1면)',
    wallCount: 1,
    walls: ['front'],
    description: '정면 벽 1개만 사용하는 단순한 구조'
  },
  {
    name: 'ㄱ자',
    label: 'ㄱ자형 (2면)',
    wallCount: 2,
    walls: ['front', 'right'],
    description: '정면과 우측 벽 2개를 사용하는 L자 구조'
  },
  {
    name: 'ㄷ자',
    label: 'ㄷ자형 (3면)',
    wallCount: 3,
    walls: ['left', 'front', 'right'],
    description: '좌측, 정면, 우측 벽 3개를 사용하는 U자 구조'
  }
];
