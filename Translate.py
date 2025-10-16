import os
import time
import google.generativeai as genai

# ==============================================================================
# ⚙️ 1. 사용자 설정
# ==============================================================================
# Gemini API 키를 입력해주세요.
GEMINI_API_KEY = "AIzaSyDvseh5Nj9xhowd78o-L98fr0s3q7xpkB8" # ⬅️⬅️⬅️ 여기에 본인의 Gemini API 키를 입력하세요!

# 이전 스크립트에서 생성된 파일들이 있는 기본 경로를 지정합니다.
BASE_PATH = r"C:\Users\82108\OneDrive\바탕 화면\4-2학기\종합설계\Modern_Language_Api"
FOLDERS = [0, 1, 2, 3, 4]       # 작업할 폴더 번호 목록
RESPONSES = list(range(1, 11)) # 번역할 파일 번호 (Response_1 ~ Response_10)

# ==============================================================================
# ⚙️ 2. Gemini 모델 및 번역 함수 설정
# ==============================================================================
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # 번역 작업에 적합한 모델을 설정합니다.
    translation_model = genai.GenerativeModel('gemini-2.5-flash')
    print("✅ Gemini 모델 초기화 성공!")
except Exception as e:
    print(f"❌ API 키 설정 또는 모델 초기화 실패: {e}")
    print("   스크립트 상단의 GEMINI_API_KEY 변수를 올바르게 설정했는지 확인해주세요.")
    exit()


def translate_text_with_gemini(text_to_translate: str) -> str:
    """Gemini API를 사용하여 주어진 텍스트를 한국어로 번역합니다."""
    if not text_to_translate.strip():
        return "" # 번역할 내용이 없으면 빈 문자열 반환

    # Gemini에 보낼 프롬프트를 구성합니다.
    # 이렇게 명시적으로 요청하면 고대 영어나 다른 언어도 잘 처리합니다.
    prompt = f"Translate the following text into Korean:\n\n---\n\n{text_to_translate}"

    try:
        # Gemini API 호출
        response = translation_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"    ❌ Gemini API 호출 중 번역 오류 발생: {e}")
        return None # 오류 발생 시 None을 반환

# ==============================================================================
# ⚙️ 3. 배치 번역 함수
# ==============================================================================
def batch_translate():
    """모든 폴더의 Response 파일을 순회하며 번역하고 새 파일로 저장합니다."""

    total_files_processed = 0
    successful_translations = 0

    for folder_num in FOLDERS:
        folder_path = os.path.join(BASE_PATH, f"Harmful_Test_{folder_num}")

        if not os.path.exists(folder_path):
            print(f"⚠️  폴더를 찾을 수 없습니다: {folder_path}")
            continue

        print(f"\n{'='*70}")
        print(f"📁 폴더 작업 시작: {folder_path}")
        print(f"{'='*70}")

        for response_num in RESPONSES:
            source_file_name = f"Response_{response_num}.txt"
            source_file_path = os.path.join(folder_path, source_file_name)

            if not os.path.exists(source_file_path):
                print(f"  ↪︎ {source_file_name}: 원본 파일 없음 (건너뛰기)")
                continue

            total_files_processed += 1
            print(f"  📄 {source_file_name} 작업 중...")

            try:
                with open(source_file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
            except Exception as e:
                print(f"    ❌ 파일 읽기 실패: {e}")
                continue

            # Gemini API로 내용 번역하기
            translated_content = translate_text_with_gemini(original_content)

            if translated_content is not None:
                dest_file_name = f"Translate_Response_{response_num}.txt"
                dest_file_path = os.path.join(folder_path, dest_file_name)
                try:
                    with open(dest_file_path, 'w', encoding='utf-8') as f:
                        f.write(translated_content)
                    print(f"    ✅ 번역 완료 및 '{dest_file_name}'으로 저장 성공!")
                    successful_translations += 1
                except Exception as e:
                    print(f"    ❌ 번역된 파일 저장 실패: {e}")
            else:
                print(f"    ↪︎ 번역에 실패하여 파일을 생성하지 않습니다.")

            # API 속도 제한을 피하기 위해 잠시 대기
            time.sleep(1)
            
    return total_files_processed, successful_translations

# ==============================================================================
# ⚙️ 4. 메인 실행
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Gemini API를 사용하여 모든 Response 파일의 배치 번역을 시작합니다...")
    
    total_files, success_count = batch_translate()
    
    print(f"\n\n{'='*70}")
    print("🏁 모든 작업 완료!")
    print(f"총 {total_files}개의 파일을 처리했으며, 그 중 {success_count}개의 번역에 성공했습니다.")
    print("각 폴더에서 'Translate_Response_...'로 시작하는 파일을 확인하세요.")
    print(f"{'='*70}")
