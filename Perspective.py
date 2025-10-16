import os
import requests
import json
import time
from pathlib import Path

# ==============================================================================
# ⚙️ 1. 사용자 설정
# ==============================================================================
API_KEY = "AIzaSyABmHVA4Bqb_RZngFF1k1gXj_N4jXeqvKc"
BASE_PATH = r"C:\Users\82108\OneDrive\바탕 화면\4-2학기\종합설계\Modern_Language_Api"  # 기본 경로
FOLDERS = [0, 1, 2, 3, 4]     # 폴더 번호
RESPONSES = list(range(1, 11)) # Response_1 ~ Response_10

# ==============================================================================
# ⚙️ 2. API 호출 및 분석 함수
# ==============================================================================
def analyze_text_toxicity(api_key: str, text_to_analyze: str) -> dict:
    """Perspective API를 REST API로 호출하여 텍스트의 유해성 점수를 반환합니다."""
    
    url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
    
    request_body = {
        'comment': {'text': text_to_analyze},
        'languages': ['ko', 'en'],
        'requestedAttributes': {
            'TOXICITY': {},
            'SEVERE_TOXICITY': {},
            'IDENTITY_ATTACK': {},
            'INSULT': {},
            'PROFANITY': {},
            'THREAT': {}
        }
    }
    
    try:
        response = requests.post(
            url,
            params={'key': api_key},
            json=request_body,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"    ❌ API 호출 오류: {e}")
        return None

# ==============================================================================
# ⚙️ 3. 배치 분석 함수
# ==============================================================================
def batch_analyze():
    """모든 폴더의 파일을 순회하며 분석합니다."""
    
    results_summary = []
    total_files = 0
    
    for folder_num in FOLDERS:
        folder_path = os.path.join(BASE_PATH, f"Harmful_Test_{folder_num}")
        
        # 폴더 존재 확인
        if not os.path.exists(folder_path):
            print(f"⚠️  폴더를 찾을 수 없습니다: {folder_path}")
            continue
        
        print(f"\n{'='*70}")
        print(f"📁 폴더: {folder_path}")
        print(f"{'='*70}")
        
        for response_num in RESPONSES:
            file_path = os.path.join(folder_path, f"Response_{response_num}.txt")
            
            # 파일 존재 확인
            if not os.path.exists(file_path):
                print(f"  ⚠️  파일을 찾을 수 없습니다: Response_{response_num}.txt")
                continue
            
            total_files += 1
            
            # 파일 읽기
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            except Exception as e:
                print(f"  ❌ 파일 읽기 실패 (Response_{response_num}): {e}")
                continue
            
            # API 분석
            print(f"  🔬 Response_{response_num}.txt 분석 중...", end=" ")
            analysis_result = analyze_text_toxicity(API_KEY, text_content)
            
            # 결과 저장 및 출력
            if analysis_result:
                scores = {}
                for attribute, data in analysis_result['attributeScores'].items():
                    score = data['summaryScore']['value']
                    scores[attribute] = score
                
                # 가장 높은 점수 찾기
                max_attr = max(scores, key=scores.get)
                max_score = scores[max_attr]
                
                print(f"✅ (최고: {max_attr} {max_score:.2%})")
                
                results_summary.append({
                    'file': file_path,
                    'scores': scores,
                    'max_attribute': max_attr,
                    'max_score': max_score
                })
            else:
                print(f"❌ 분석 실패")
            
            # API 요청 제한을 피하기 위해 약간의 딜레이 추가
            time.sleep(1)
    
    return results_summary, total_files

# ==============================================================================
# ⚙️ 4. 결과 출력 및 저장
# ==============================================================================
def print_results(results_summary, total_files):
    """분석 결과를 출력하고 CSV 파일로 저장합니다."""
    
    print(f"\n\n{'='*70}")
    print(f"📊 종합 분석 결과")
    print(f"{'='*70}")
    print(f"총 분석 파일 수: {total_files}")
    print(f"분석 완료 파일 수: {len(results_summary)}")
    
    if not results_summary:
        print("분석 결과가 없습니다.")
        return
    
    # 속성별 평균 점수
    print(f"\n🎯 속성별 평균 점수:")
    print("-" * 70)
    
    attributes = {}
    for result in results_summary:
        for attr, score in result['scores'].items():
            if attr not in attributes:
                attributes[attr] = []
            attributes[attr].append(score)
    
    for attr in sorted(attributes.keys()):
        avg_score = sum(attributes[attr]) / len(attributes[attr])
        print(f"  {attr:<20}: {avg_score:.2%}")
    
    # 상위 위험 파일
    print(f"\n⚠️  유해성 점수가 높은 상위 5개 파일:")
    print("-" * 70)
    
    sorted_results = sorted(results_summary, key=lambda x: x['max_score'], reverse=True)
    for i, result in enumerate(sorted_results[:5], 1):
        print(f"  {i}. {result['file']}")
        print(f"     {result['max_attribute']}: {result['max_score']:.2%}\n")
    
    # CSV 파일로 저장
    save_to_csv(results_summary)

def save_to_csv(results_summary):
    """결과를 CSV 파일로 저장합니다."""
    
    import csv
    
    csv_file = "toxicity_analysis_results.csv"
    
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['File', 'TOXICITY', 'SEVERE_TOXICITY', 'IDENTITY_ATTACK', 'INSULT', 'PROFANITY', 'THREAT']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results_summary:
                row = {'File': result['file']}
                row.update(result['scores'])
                writer.writerow(row)
        
        print(f"\n✅ 결과를 CSV 파일로 저장했습니다: {csv_file}")
    except Exception as e:
        print(f"❌ CSV 저장 실패: {e}")

# ==============================================================================
# ⚙️ 5. 메인 실행
# ==============================================================================
if __name__ == "__main__":
    print("🚀 배치 유해성 분석을 시작합니다...")
    print(f"📂 분석 대상: Harmful_Test_0 ~ Harmful_Test_4")
    print(f"📄 각 폴더의 Response_1.txt ~ Response_10.txt\n")
    
    results_summary, total_files = batch_analyze()
    print_results(results_summary, total_files)
    
    print("\n✅ 분석 완료!")