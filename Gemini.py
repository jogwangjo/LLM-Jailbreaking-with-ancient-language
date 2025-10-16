import google.generativeai as genai
import os
import time

GEMINI_API_KEY = "AIzaSyBdaW2FPtmDZXU-rpwndpWFAxsqtBg32s4"  # 본인의 API 키를 입력하세요

# ==============================================================================
# ⚙️ 1. 프롬프트 파일에서 불러오기
# ==============================================================================

JAILBREAK_PROMPTS = []
PROMPT_FILENAME = "prompts.txt"
PROMPT_SEPARATOR = "---PROMPT_SEPARATOR---"

try:
    with open(PROMPT_FILENAME, 'r', encoding='utf-8') as f:
        content = f.read()
    # 구분자를 기준으로 텍스트를 나누고, 각 프롬프트의 양쪽 공백을 제거합니다.
    # 내용이 비어있는 부분은 리스트에 추가하지 않습니다.
    JAILBREAK_PROMPTS = [p.strip() for p in content.split(PROMPT_SEPARATOR) if p.strip()]
    
    if not JAILBREAK_PROMPTS:
        print(f"❌ '{PROMPT_FILENAME}' 파일은 있으나 내용이 비어있거나 구분자가 없습니다.")
        exit()
    else:
        print(f"✅ '{PROMPT_FILENAME}' 파일에서 총 {len(JAILBREAK_PROMPTS)}개의 프롬프트를 성공적으로 불러왔습니다.")

except FileNotFoundError:
    print(f"❌ '{PROMPT_FILENAME}' 파일을 찾을 수 없습니다. 스크립트와 같은 경로에 파일을 만들어주세요.")
    exit()
except Exception as e:
    print(f"❌ 파일을 읽는 중 오류가 발생했습니다: {e}")
    exit()


NUM_REPEATS = 10  # 각 프롬프트당 반복할 횟수

# ==============================================================================
# ⚙️ 2. 모델 및 환경 설정
# ==============================================================================

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash') 
    print("✅ 모델 초기화 성공!")
except Exception as e:
    print(f"❌ API 키 설정 또는 모델 초기화 실패: {e}")
    exit()

# 안전 설정을 'BLOCK_NONE'으로 지정
safety_settings = {
    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
}

# ==============================================================================
# ⚙️ 3. 메인 실행 로직
# ==============================================================================

print(f"\n총 {len(JAILBREAK_PROMPTS)}개의 프롬프트에 대해 각각 {NUM_REPEATS}회 응답 생성을 시작합니다.")

# --- 모든 프롬프트를 순회하며 테스트 실행 ---
for prompt_index, current_prompt in enumerate(JAILBREAK_PROMPTS):

    # 1. 프롬프트 내용 확인 (파일 로드 시 이미 처리되었지만, 안전을 위해 유지)
    if not current_prompt.strip():
        print(f"\n[프롬프트 {prompt_index + 1}/{len(JAILBREAK_PROMPTS)}] 내용이 비어있어 건너뜁니다.")
        continue

    # 2. 폴더 이름 설정 (Harmful_Test_0, Harmful_Test_1, ...)
    CURRENT_FOLDER_NAME = f"Harmful_Test_{prompt_index}"

    print(f"\n=======================================================")
    print(f"[프롬프트 {prompt_index + 1}/{len(JAILBREAK_PROMPTS)}] : 폴더 '{CURRENT_FOLDER_NAME}' 생성 및 테스트 시작")
    print(f"=======================================================")

    os.makedirs(CURRENT_FOLDER_NAME, exist_ok=True)

    # 3. 입력된 프롬프트를 Prompt.txt 파일로 저장
    prompt_txt_path = os.path.join(CURRENT_FOLDER_NAME, "Prompt.txt")
    try:
        with open(prompt_txt_path, 'w', encoding='utf-8') as f:
            f.write(current_prompt)
    except Exception as e:
        print(f"      - Prompt.txt 저장 실패: {e}")

    # 4. 지정된 횟수만큼 반복 실행
    for i in range(NUM_REPEATS):
        print(f"--- [응답 생성 {i+1}/{NUM_REPEATS}] ---")

        try:
            # API 호출 시 안전 설정 포함
            response = model.generate_content(
                current_prompt,
                safety_settings=safety_settings
            )

            # 응답 텍스트를 파일에 저장
            filename = f"Response_{i+1}.txt"
            full_path = os.path.join(CURRENT_FOLDER_NAME, filename)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"      -> ✅ 성공! 응답을 '{full_path}' 파일에 저장했습니다.")

        except ValueError:
            # .text 접근 시 응답이 차단되어 발생하는 오류 처리
            print(f"      -> ❌ 실패! 응답이 안전 설정에 의해 차단되었습니다.")
        except Exception as e:
            # 기타 API 오류 또는 네트워크 문제 처리
            print(f"      -> ❌ 실패! API 호출 중 오류 발생: {e}")

        # 마지막 반복이 아니면 잠시 대기
        if i < NUM_REPEATS - 1:
            time.sleep(1)

print(f"\n\n🏁 모든 작업 완료! 생성된 폴더에서 결과를 확인하세요.")