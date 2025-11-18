"""
input_images 컬럼의 NULL 및 빈 객체를 빈 배열로 수정하는 스크립트
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


def fix_input_images():
    """NULL이나 빈 객체인 input_images를 빈 배열로 수정"""
    print("🔄 input_images 컬럼 수정 시작...")

    with get_db_cursor() as cursor:
        # NULL 값을 빈 배열로 변경
        cursor.execute("""
            UPDATE prompts
            SET input_images = '[]'::jsonb
            WHERE input_images IS NULL
        """)
        null_count = cursor.rowcount
        print(f"✅ NULL → [] 변환: {null_count}개")

        # 빈 객체를 빈 배열로 변경
        cursor.execute("""
            UPDATE prompts
            SET input_images = '[]'::jsonb
            WHERE input_images = '{}'::jsonb
        """)
        empty_obj_count = cursor.rowcount
        print(f"✅ {{}} → [] 변환: {empty_obj_count}개")

        # 검증: 모든 input_images가 배열인지 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM prompts
            WHERE jsonb_typeof(input_images) != 'array'
              AND delete_yn = 0
        """)
        invalid_count = cursor.fetchone()[0]

        if invalid_count > 0:
            print(f"⚠️ 경고: {invalid_count}개의 레코드가 여전히 배열이 아닙니다.")
        else:
            print(f"✅ 검증 완료: 모든 input_images가 배열 타입입니다.")

        print(f"\n📊 결과 요약:")
        print(f"   - NULL 변환: {null_count}개")
        print(f"   - 빈 객체 변환: {empty_obj_count}개")
        print(f"   - 총 수정: {null_count + empty_obj_count}개")
        print("\n✨ 완료!")


if __name__ == "__main__":
    fix_input_images()
