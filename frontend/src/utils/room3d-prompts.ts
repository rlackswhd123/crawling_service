/**
 * @deprecated DEPRECATED: This file is no longer used.
 *
 * Room 3D prompts are now managed in the database with structure-specific
 * default prompts (ㅡ-shape, ㄱ-shape, ㄷ-shape).
 *
 * Use PromptEditor component which loads prompts from the database via
 * prompt_kind: 'bangkku/3d-room-generator/{shape}'
 *
 * Migration Date: 2025-01-28
 * Reason: Move from code-generated prompts to DB-first approach for consistency
 * with other features (furniture removal, front view, video generation)
 */

/**
 * Room 3D Prompt Generation Utility
 * 방 구조에 따른 동적 프롬프트 생성
 */

import type { RoomStructure } from '@/types/room3d.types';

interface PromptComponents {
  layoutDescription: string;
  cameraAngle: string;
  wallCountWarning: string;
  imageDescriptions: string;
}

/**
 * 방 구조에 따른 프롬프트 컴포넌트 생성
 */
function getPromptComponents(structure: RoomStructure, surfaceCount: number): PromptComponents {
  let layoutDescription = '';
  let cameraAngle = '';
  let wallCountWarning = '';
  let imageDescriptions = '';

  switch (structure) {
    case 'ㅡ자':
      layoutDescription = 'ㅡ자 형태 - 정면 벽 1개만 (총 1개)';
      cameraAngle = '정면 중앙에서 바라보는 시점';
      wallCountWarning = '⚠️ 정확히 1개 벽면만 사용. 좌측/우측 벽 절대 생성 금지';
      imageDescriptions = `- 이미지 1: 정면 벽면 가구 배치도`;
      break;

    case 'ㄱ자':
      layoutDescription = 'ㄱ자 형태 - 정면 벽 + 우측 벽 (총 2개)';
      cameraAngle = '정면 좌측에서 바라보는 시점 (두 벽면이 모두 보이도록)';
      wallCountWarning = '⚠️ 정확히 2개 벽면만 사용. 추가 벽 생성 절대 금지';
      imageDescriptions = `- 이미지 1: 정면 벽면 가구 배치도
- 이미지 2: 우측 벽면 가구 배치도`;
      break;

    case 'ㄷ자':
      layoutDescription = 'ㄷ자 형태 - 좌측 벽 + 정면 벽 + 우측 벽 (총 3개)';
      cameraAngle = '정면 중앙에서 바라보는 시점 (세 벽면이 모두 보이도록)';
      wallCountWarning = '⚠️ 정확히 3개 벽면만 사용. 뒤쪽 벽 절대 생성 금지';
      imageDescriptions = `- 이미지 1: 좌측 벽면 가구 배치도
- 이미지 2: 정면 벽면 가구 배치도
- 이미지 3: 우측 벽면 가구 배치도`;
      break;

    default:
      layoutDescription = `${structure} - ${surfaceCount}개 벽면`;
      cameraAngle = '정면 중앙에서 바라보는 시점';
      wallCountWarning = `⚠️ 정확히 ${surfaceCount}개 벽면만 사용`;
      imageDescriptions = Array.from(
        { length: surfaceCount },
        (_, i) => `- 이미지 ${i + 1}: ${i + 1}면 벽면 가구 배치도`
      ).join('\n');
  }

  return {
    layoutDescription,
    cameraAngle,
    wallCountWarning,
    imageDescriptions
  };
}

/**
 * 방 구조에 따른 완전한 프롬프트 생성
 *
 * @param structure - 방 구조 (ㅡ자, ㄱ자, ㄷ자)
 * @param surfaceCount - 벽면 이미지 개수
 * @returns 생성된 프롬프트 텍스트
 */
export function generatePromptForStructure(
  structure: RoomStructure,
  surfaceCount: number
): string {
  const { layoutDescription, cameraAngle, wallCountWarning, imageDescriptions } =
    getPromptComponents(structure, surfaceCount);

  const lastImageNum = surfaceCount + 1;

  return `**참조 이미지 구성:**
${imageDescriptions}
- 이미지 ${lastImageNum}: 배경으로 사용할 빈 방 (벽, 바닥, 조명 분위기 참조)

**작업 내용:**
제공된 ${surfaceCount}개의 벽면 가구 배치도를 이미지 ${lastImageNum}의 공간 안에 배치하여
사실적인 3D 드레스룸/수납공간 렌더링을 제작해주세요.

**배치 형태:**
${layoutDescription}
${wallCountWarning}

**카메라 앵글 (중요):**
${cameraAngle}

**절대 원칙 (위반 시 작업 실패):**
1. **벽면 개수 엄수**: 정확히 ${surfaceCount}개 벽면만 사용. 제공되지 않은 벽면 생성 절대 금지
2. **원본 충실도**: 각 벽면 이미지의 구조, 비율, 아이템 배치를 정확하게 유지
3. **변형 금지**: 임의 수정, 재해석, 창작적 변형 절대 금지
4. **디테일 일치**: 모든 선반, 서랍, 도어, 장식품이 원본 이미지와 정확히 일치

**각 벽면 가구의 공통 특징:**
- 베이지/크림색 금속 프레임 또는 원목 프레임
- 원목 선반 (따뜻한 갈색 톤)
- 회색, 베이지, 흰색 서랍 및 도어
- 실용적인 수납 구조
- 깔끔하고 모던한 디자인

**렌더링 세부사항:**
- 배경 이미지(이미지 ${lastImageNum})의 조명, 벽 질감, 바닥을 그대로 활용
- 전체 구성이 잘리지 않고 완전히 보이도록
- 과도한 광각이나 왜곡 없이 건축 사진처럼 정돈된 구도
- **모든 가구는 바닥에 정확히 닿아있어야 함 (공중에 떠있거나 부유하는 가구 절대 금지)**
- 가구는 벽면과 바닥에 실제로 설치된 것처럼 고정된 상태로 렌더링
- 가구는 벽면 이미지를 정확히 따르고, 공간은 배경 이미지를 따름
- **제공된 ${surfaceCount}개 벽면만 렌더링, 추가 벽면 생성 금지**

**필수 조건:**
- 모든 텍스트, 버튼, 치수 표시, UI 요소 완전 제거
- 순수하게 가구와 공간만 보이는 깨끔한 인테리어 렌더링
- 실제 촬영한 드레스룸/수납공간 사진처럼 자연스럽게 표현

**결과물:**
${structure}의 드레스룸/수납공간 전체 (정확히 ${surfaceCount}개 벽면), 16:9 비율, 고해상도`;
}
