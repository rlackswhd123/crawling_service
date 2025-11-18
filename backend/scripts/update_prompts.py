"""
프롬프트를 업데이트하는 스크립트
기존 default 프롬프트의 내용을 새로운 한글 버전으로 업데이트
"""

import sys
import io
from pathlib import Path

# Windows 인코딩 문제 해결: UTF-8 강제
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import get_db_cursor


# 업데이트할 프롬프트 데이터
PROMPT_UPDATES = [
    {
        "prompt_kind": "bangkku/furniture-removal",
        "new_text": """단계 1: 이 이미지에서 모든 가구와 수납 시스템을 제거합니다
단계 2: 빈 공간을 평범한 벽과 바닥으로 채웁니다
단계 3: 좌측과 우측 벽이 완전히 비어있고 선반이 남아있지 않은지 확인합니다

완전히 제거해야 할 것:
- 모든 선반 유닛과 프레임 (좌측 벽, 우측 벽, 중앙 벽)
- 양쪽의 모든 원목 선반과 봉
- 모든 수납장과 서랍
- 모든 수직 및 수평 지지대
- 선반 위의 모든 물건 (수건, 상자, 신발, 바구니)
- 모든 수납 시스템과 설비

중요: 좌측과 우측 측면 벽에 특별히 주의하세요 - 완전히 비어있어야 합니다!

최종 결과:
- 완전히 비어있는 직사각형 방
- 평범한 흰색/베이지색 벽만 (네 개의 벽 모두 - 좌측, 우측, 정면, 후면)
- 같은 질감의 빈 바닥
- 빈 천장
- 어떤 벽에도 부착물이나 설비 없음
- 옷장이 설치되기 전의 가구 없는 방처럼"""
    },
    {
        "prompt_kind": "bangkku/furniture-front-view",
        "new_text": """이 가구 이미지를 전문적인 스튜디오 조명으로 정면 촬영으로 변환하세요. 부드럽고 확산된 상단-정면 조명(45도 각도)을 사용하여 미묘한 그림자를 만들고 모든 디테일을 강조하세요. 가구의 정확한 디자인, 색상, 재질을 유지하면서, 균일하고 중립적인 조명의 전문 제품 사진 스튜디오에서 촬영한 것처럼 완벽한 정면 시점에서 보여주세요."""
    },
    {
        "prompt_kind": "bangkku/video-generation",
        "new_text": """1인칭 시점(POV)에서 현대적이고 미니멀한 드레스룸 내부를 보여주는 10초, 단일 테이크 영화적 비디오입니다.
카메라는 항상 정면을 향한 채로 유지되며, 뒤돌아보지 않습니다.
방 안으로 부드럽게 이동하며, 좌측, 중앙, 우측 섹션을 미묘하게 탐색한 다음, 원래의 입구 위치로 부드럽게 돌아옵니다 — 모두 하나의 연속적이고 매끄러운 움직임으로 이루어집니다.
움직임은 유연하고, 안정적이며, 자연스러워야 하며, 갑작스러운 컷이나 회전 없어야 합니다.

[0–2.5초]
카메라가 입구에서 약간 앞으로 전진하며, 방의 명확하고 넓은 시야를 유지합니다.
따뜻하고 균일한 조명이 깨끗하고 현대적인 레이아웃, 베이지 톤, 목재 질감을 드러냅니다.

[2.5–4.5초]
제자리에 머무르면서, 카메라가 천천히 좌측으로 패닝하여 옷장, 서랍, 의류 디테일을 부드럽고 섬세한 움직임으로 관찰합니다.
카메라의 몸체는 회전하지 않고 — 시선만 부드럽게 좌측으로 이동합니다.

[4.5–7.0초]
시야가 중앙 섹션으로 부드럽게 전환되어, 중간 선반, 조명 악센트, 균형 잡힌 대칭을 천천히 수평으로 움직이며 강조합니다.

[7.0–9.0초]
시선이 우측으로 계속 이어지며, 정면을 향한 채로 뒤돌아보지 않고 "ㄷ"자형 옷장 레이아웃의 자연스러운 흐름을 부드럽게 따라갑니다.

[9.0–10.0초]
카메라가 입구 근처의 시작 위치로 부드럽게 뒤로 이동하며, 같은 정면 방향을 유지합니다.
이는 카메라 회전 없이 미묘한 역방향 복귀 효과를 만듭니다.

조명은 부드럽고, 따뜻하며, 균일하게 분산되어 공간의 차분하고 고급스러운 미니멀리스트 분위기를 강조해야 합니다.

⚠️ 중요:

제공된 참조 이미지에서 보이지 않는 물체를 추가하거나, 제거하거나, 수정하지 마세요.

비디오는 이미지의 레이아웃에 완전히 충실해야 합니다 — 새로운 가구, 누락된 항목, 장면 변경이 없어야 합니다.

카메라는 절대 뒤돌아보거나 회전해서는 안 됩니다; 같은 방향을 유지하면서 좌우로 패닝하고 약간 앞뒤로 이동하기만 합니다."""
    }
]


def update_prompts():
    """기존 프롬프트를 새로운 내용으로 업데이트"""
    print("🔄 프롬프트 업데이트 시작...")

    with get_db_cursor() as cursor:
        updated_count = 0
        not_found_count = 0

        for update_data in PROMPT_UPDATES:
            prompt_kind = update_data["prompt_kind"]

            # 기존 프롬프트 확인
            cursor.execute("""
                SELECT prompt_key
                FROM prompts
                WHERE prompt_kind = %s AND is_default_yn = 1 AND delete_yn = 0
            """, (prompt_kind,))

            existing = cursor.fetchone()

            if not existing:
                print(f"❌ 찾을 수 없음: {prompt_kind}")
                not_found_count += 1
                continue

            prompt_key = existing['prompt_key']

            # 프롬프트 업데이트
            cursor.execute("""
                UPDATE prompts
                SET prompt_text = %s,
                    upd_date = CURRENT_TIMESTAMP
                WHERE prompt_key = %s
            """, (update_data["new_text"], prompt_key))

            print(f"✅ 업데이트 완료: {prompt_kind} (Key: {prompt_key})")
            updated_count += 1

        print(f"\n📊 결과 요약:")
        print(f"   - 업데이트됨: {updated_count}개")
        print(f"   - 찾을 수 없음: {not_found_count}개")
        print(f"   - 총: {len(PROMPT_UPDATES)}개")
        print("\n✨ 완료!")


if __name__ == "__main__":
    update_prompts()
