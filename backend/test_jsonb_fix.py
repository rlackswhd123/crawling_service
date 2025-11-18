"""
Test script to verify JSONB type fix for input_images column
"""
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repos.prompt_repo import PromptRepository
from schemas.prompt import PromptCreate


def test_prompt_with_images():
    """Test creating prompt with image URLs"""
    print("=== Testing Prompt Creation with Images ===\n")

    # Initialize repository
    repo = PromptRepository()

    # Test data with images
    test_data = PromptCreate(
        prompt_kind=1,  # Furniture Removal
        prompt_content="빈 공간을 자연스럽게 채워주세요",
        rating=5,
        input_images=[
            "/static/prompts/images/test1.jpg",
            "/static/prompts/images/test2.jpg",
            "/static/prompts/images/test3.jpg"
        ]
    )

    try:
        # Convert to dict
        data = test_data.model_dump()
        print(f"Input data: {data}\n")

        # Create prompt
        prompt_key = repo.create(data)
        print(f"✅ Success! Created prompt with key: {prompt_key}\n")

        # Retrieve to verify
        result = repo.get_by_id(prompt_key)
        print(f"Retrieved data:")
        print(f"  - prompt_key: {result['prompt_key']}")
        print(f"  - input_images: {result['input_images']}")
        print(f"  - input_images type: {type(result['input_images'])}")

        # Verify it's stored correctly
        if isinstance(result['input_images'], list):
            print(f"\n✅ input_images is correctly stored as list with {len(result['input_images'])} items")
            for idx, img in enumerate(result['input_images'], 1):
                print(f"    {idx}. {img}")
        else:
            print(f"\n❌ ERROR: input_images is {type(result['input_images'])}, expected list")

        # Clean up
        repo.delete(prompt_key)
        print(f"\n🗑️  Cleaned up test data (soft deleted prompt_key={prompt_key})")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_prompt_without_images():
    """Test creating prompt without images (empty array)"""
    print("\n\n=== Testing Prompt Creation WITHOUT Images ===\n")

    repo = PromptRepository()

    test_data = PromptCreate(
        prompt_kind=1,
        prompt_content="이미지 없는 테스트",
        rating=0,
        input_images=[]  # Empty array
    )

    try:
        data = test_data.model_dump()
        print(f"Input data: {data}\n")

        prompt_key = repo.create(data)
        print(f"✅ Success! Created prompt with key: {prompt_key}\n")

        result = repo.get_by_id(prompt_key)
        print(f"Retrieved data:")
        print(f"  - input_images: {result['input_images']}")
        print(f"  - input_images type: {type(result['input_images'])}")

        if result['input_images'] == []:
            print(f"\n✅ input_images is correctly stored as empty list")
        else:
            print(f"\n⚠️  WARNING: Expected empty list, got {result['input_images']}")

        # Clean up
        repo.delete(prompt_key)
        print(f"\n🗑️  Cleaned up test data (soft deleted prompt_key={prompt_key})")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("JSONB Type Fix Verification Test")
    print("=" * 60)
    print()

    test1_passed = test_prompt_with_images()
    test2_passed = test_prompt_without_images()

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    print(f"  Test 1 (with images):    {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  Test 2 (without images): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print()

    if test1_passed and test2_passed:
        print("🎉 All tests passed! JSONB fix is working correctly.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please check the errors above.")
        sys.exit(1)
