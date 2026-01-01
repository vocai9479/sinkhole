#!/usr/bin/env python3
"""
SafeGround AI - evalNm 파싱 테스트 스크립트

API-7의 evalNm (평가명) 필드에서 위치 정보 추출 테스트:
- 시도(city) 추출 성공률
- 시군구(district) 추출 성공률
- 읍면동(dong) 추출 성공률

목표: 70% 이상 파싱 성공 → 전체 수집 GO
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter

# 데이터 저장 경로
DATA_DIR = Path("data/sample")

# 서울시 행정동 데이터 로드
SEOUL_DONG_FILE = Path("data/seoul_424dong.csv")


def load_seoul_dongs() -> Dict[str, List[str]]:
    """
    서울시 424개 행정동 데이터 로드

    Returns:
        {
            '구': ['동1', '동2', ...],
            ...
        }
    """
    dongs_by_district = {}

    if not SEOUL_DONG_FILE.exists():
        print(f"✗ 행정동 데이터 파일 없음: {SEOUL_DONG_FILE}")
        return {}

    with open(SEOUL_DONG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]  # Skip header

    for line in lines:
        parts = line.strip().split(',')
        if len(parts) >= 3:
            district = parts[1]  # 구
            dong = parts[2]      # 동

            if district not in dongs_by_district:
                dongs_by_district[district] = []

            dongs_by_district[district].append(dong)

    print(f"✓ 서울시 행정동 데이터 로드: {len(dongs_by_district)}개 구")
    return dongs_by_district


def extract_location_from_evalNm(eval_nm: str, seoul_dongs: Dict[str, List[str]]) -> Dict[str, str]:
    """
    evalNm에서 위치 정보 추출 (휴리스틱)

    Args:
        eval_nm: 평가명 (예: "포천동성남시탄리(1,2공사) 향후계획서의 설치공사")
        seoul_dongs: 서울시 행정동 딕셔너리

    Returns:
        {
            'city': '서울특별시',
            'district': '강남구',
            'dong': '역삼동',
            'confidence': 'high/medium/low'
        }
    """
    location = {
        'city': None,
        'district': None,
        'dong': None,
        'confidence': 'low'
    }

    # 패턴 정의
    city_pattern = r'(서울|부산|대구|인천|광주|대전|울산|세종)'
    district_pattern = r'([가-힣]+구)'
    dong_pattern = r'([가-힣]+동|[가-힣]+읍|[가-힣]+면)'

    # 1. 시도 추출
    city_match = re.search(city_pattern, eval_nm)
    if city_match:
        city = city_match.group(1)
        if city == '서울':
            location['city'] = '서울특별시'
        else:
            location['city'] = city

    # 2. 시군구 추출 (서울시 구 우선)
    district_matches = re.findall(district_pattern, eval_nm)
    if district_matches:
        # 서울시 구인지 확인
        for district in district_matches:
            if district in seoul_dongs:
                location['district'] = district
                location['city'] = '서울특별시'  # 서울시 구 발견 시 city도 업데이트
                break

        # 서울시 구가 아니면 첫 번째 매치
        if not location['district']:
            location['district'] = district_matches[0]

    # 3. 읍면동 추출
    dong_matches = re.findall(dong_pattern, eval_nm)
    if dong_matches and location['district']:
        # 해당 구의 동 리스트 확인
        valid_dongs = seoul_dongs.get(location['district'], [])

        for dong in dong_matches:
            if dong in valid_dongs:
                location['dong'] = dong
                location['confidence'] = 'high'
                break

        # 유효한 동이 없으면 첫 번째 매치
        if not location['dong'] and dong_matches:
            location['dong'] = dong_matches[0]
            location['confidence'] = 'medium'

    # 신뢰도 조정
    if location['city'] and location['district'] and location['dong']:
        if location['confidence'] != 'high':
            location['confidence'] = 'medium'
    elif location['city'] or location['district']:
        location['confidence'] = 'low'

    return location


def test_parsing_on_samples(eval_names: List[str], seoul_dongs: Dict[str, List[str]]) -> Dict:
    """
    샘플 evalNm 리스트로 파싱 테스트

    Args:
        eval_names: evalNm 리스트
        seoul_dongs: 서울시 행정동 딕셔너리

    Returns:
        파싱 결과 통계
    """
    results = []

    print("\n" + "="*80)
    print("🧪 evalNm 파싱 테스트")
    print("="*80)

    for idx, eval_nm in enumerate(eval_names, 1):
        location = extract_location_from_evalNm(eval_nm, seoul_dongs)

        result = {
            'eval_nm': eval_nm,
            'city': location['city'],
            'district': location['district'],
            'dong': location['dong'],
            'confidence': location['confidence']
        }
        results.append(result)

        # 출력
        city_str = location['city'] or '✗'
        district_str = location['district'] or '✗'
        dong_str = location['dong'] or '✗'
        confidence_str = location['confidence']

        print(f"\n[{idx}] {eval_nm}")
        print(f"  → 시도: {city_str}")
        print(f"  → 구:   {district_str}")
        print(f"  → 동:   {dong_str}")
        print(f"  → 신뢰도: {confidence_str}")

    return results


def calculate_success_rate(results: List[Dict]) -> Dict:
    """
    파싱 성공률 계산

    Returns:
        {
            'city_rate': 0.8,
            'district_rate': 0.7,
            'dong_rate': 0.6,
            'overall_rate': 0.5
        }
    """
    total = len(results)

    if total == 0:
        return {
            'city_rate': 0.0,
            'district_rate': 0.0,
            'dong_rate': 0.0,
            'overall_rate': 0.0
        }

    city_success = sum(1 for r in results if r['city'])
    district_success = sum(1 for r in results if r['district'])
    dong_success = sum(1 for r in results if r['dong'])
    overall_success = sum(1 for r in results if r['city'] and r['district'] and r['dong'])

    return {
        'city_rate': city_success / total * 100,
        'district_rate': district_success / total * 100,
        'dong_rate': dong_success / total * 100,
        'overall_rate': overall_success / total * 100
    }


def generate_parsing_report(results: List[Dict], success_rates: Dict):
    """파싱 테스트 리포트 생성"""
    print("\n" + "🎯"*40)
    print("📊 evalNm 파싱 테스트 결과 리포트")
    print("🎯"*40)

    total = len(results)

    print(f"\n1️⃣ 파싱 성공률 (총 {total}건)")
    print("="*60)
    print(f"  시도(city)   추출: {success_rates['city_rate']:>6.1f}%")
    print(f"  시군구(district) 추출: {success_rates['district_rate']:>6.1f}%")
    print(f"  읍면동(dong) 추출: {success_rates['dong_rate']:>6.1f}%")
    print(f"  전체(city+district+dong): {success_rates['overall_rate']:>6.1f}%")

    # 신뢰도 분포
    confidence_counts = Counter(r['confidence'] for r in results)
    print(f"\n2️⃣ 신뢰도 분포")
    print("="*60)
    for conf in ['high', 'medium', 'low']:
        count = confidence_counts.get(conf, 0)
        ratio = count / total * 100 if total > 0 else 0
        print(f"  {conf:>8}: {count:>3}건 ({ratio:>5.1f}%)")

    # 판정
    print(f"\n3️⃣ 전체 수집 여부 판정")
    print("="*60)

    threshold = 70.0
    overall_rate = success_rates['overall_rate']

    if overall_rate >= threshold:
        print(f"  ✅ 합격! 파싱 성공률 {overall_rate:.1f}% >= {threshold}%")
        print(f"  ✅ 전체 데이터 수집 진행 권장")
        print(f"\n  📌 다음 단계:")
        print(f"     1. API-7로 전체 평가 리스트 수집")
        print(f"     2. evalNm 파싱으로 위치 정보 추출")
        print(f"     3. 424개 행정동 매핑")
    else:
        print(f"  ⚠️  불합격. 파싱 성공률 {overall_rate:.1f}% < {threshold}%")
        print(f"  ⚠️  위치 정보 추출 어려움")
        print(f"\n  📌 대안:")
        print(f"     1. API-13의 dong 필드 활용 (사고 이력 데이터)")
        print(f"     2. 외부 주소 API 활용 (도로명주소 → 행정동)")
        print(f"     3. 수작업 매핑 (소량 데이터인 경우)")

    # 샘플 데이터 저장
    results_file = DATA_DIR / 'parsing_test_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'results': results,
            'success_rates': success_rates,
            'total_count': total
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 테스트 결과 저장: {results_file}")


def main():
    """메인 실행 함수"""
    print("\n" + "🧪"*40)
    print("SafeGround AI - evalNm 파싱 테스트")
    print("목표: 70% 이상 파싱 성공 → 전체 수집 GO")
    print("🧪"*40)

    # 서울시 행정동 데이터 로드
    seoul_dongs = load_seoul_dongs()

    # evalNm 샘플 로드
    eval_names_file = DATA_DIR / 'eval_names_sample.json'
    if not eval_names_file.exists():
        print(f"\n✗ evalNm 샘플 파일 없음: {eval_names_file}")
        print(f"먼저 explore_apis.py와 analyze_sample.py를 실행하세요.")
        return

    with open(eval_names_file, 'r', encoding='utf-8') as f:
        eval_names = json.load(f)

    print(f"\n✓ evalNm 샘플 로드: {len(eval_names)}건")

    # 파싱 테스트
    results = test_parsing_on_samples(eval_names, seoul_dongs)

    # 성공률 계산
    success_rates = calculate_success_rate(results)

    # 리포트 생성
    generate_parsing_report(results, success_rates)

    print("\n" + "="*80)
    print("✅ 파싱 테스트 완료!")
    print("="*80)


if __name__ == "__main__":
    main()
