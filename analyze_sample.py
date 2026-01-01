#!/usr/bin/env python3
"""
SafeGround AI - 샘플 데이터 분석 스크립트

explore_apis.py에서 수집한 샘플 데이터를 분석:
1. 전체 데이터 건수 확인
2. 연도별 분포 파악
3. dong 필드 존재 여부 확인 (API-13)
4. evalNm 샘플 수집 (파싱 테스트용)
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime

# 데이터 저장 경로
DATA_DIR = Path("data/sample")


def load_json(filename: str) -> Dict:
    """JSON 파일 로드"""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"✗ 파일 없음: {filepath}")
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_api12_subsidence_list():
    """API-12: 사고 리스트 분석"""
    print("\n" + "="*80)
    print("📊 [API-12] 지반침하사고 리스트 분석")
    print("="*80)

    data = load_json('API-12_subsidence_list.json')

    if not data:
        print("✗ 데이터 없음")
        return

    body = data.get('response', {}).get('body', {})
    total_count = body.get('totalCount', 0)
    items = body.get('items', {}).get('item', [])

    if isinstance(items, dict):
        items = [items]

    print(f"\n✅ 전체 데이터 건수: {total_count}건 (2023년 기준)")
    print(f"✅ 샘플 수집: {len(items)}건")

    # 시군구별 분포
    sigungu_counts = Counter(item.get('siGunGu', '미상') for item in items)
    print(f"\n📍 시군구별 분포 (샘플):")
    for sigungu, count in sigungu_counts.most_common(5):
        print(f"  {sigungu}: {count}건")

    # 원인별 분포
    cause_counts = Counter()
    for item in items:
        cause = item.get('sagoDetail', '확정중')
        if not cause or cause.strip() == '':
            cause = '확정중'
        cause_counts[cause] += 1

    print(f"\n🔍 사고 원인 분포 (샘플):")
    for cause, count in cause_counts.most_common(5):
        print(f"  {cause}: {count}건")

    # 날짜 분포
    dates = [item.get('sagoDate', '') for item in items if item.get('sagoDate')]
    if dates:
        years = [d[:4] for d in dates if len(d) >= 4]
        year_counts = Counter(years)
        print(f"\n📅 연도별 분포 (샘플):")
        for year in sorted(year_counts.keys()):
            print(f"  {year}년: {year_counts[year]}건")

    return {
        'total_count': total_count,
        'sample_count': len(items),
        'sigungu_distribution': dict(sigungu_counts),
        'year_distribution': dict(Counter(years)) if dates else {}
    }


def analyze_api13_subsidence_info():
    """API-13: 사고 상세정보 분석 (dong 필드 확인 핵심!)"""
    print("\n" + "="*80)
    print("📊 [API-13] 지반침하사고 상세정보 분석")
    print("="*80)

    data = load_json('API-13_subsidence_info.json')

    if not data:
        print("✗ 데이터 없음")
        return

    body = data.get('response', {}).get('body', {})
    items = body.get('items', {}).get('item', {})

    if isinstance(items, list):
        items = items[0] if items else {}

    print(f"\n✅ 샘플 수집: 1건 (상세정보)")

    # ⭐ 핵심: dong 필드 확인
    dong = items.get('dong', '')
    has_dong = bool(dong and dong.strip())

    print(f"\n⭐⭐⭐ [중요] dong 필드 존재 여부: {'✅ YES!' if has_dong else '✗ NO'}")
    if has_dong:
        print(f"  → 행정동 정보: {items.get('siDo')} {items.get('siGunGu')} {dong}")
        print(f"  → 424개 행정동 매핑 가능!")
    else:
        print(f"  → 행정동 정보 없음 (evalNm 파싱 필요)")

    # 규모 정보 확인
    print(f"\n📏 사고 규모 정보:")
    print(f"  폭: {items.get('sinkWidth', 0)}m")
    print(f"  연장: {items.get('sinkExtend', 0)}m")
    print(f"  깊이: {items.get('sinkDepth', 0)}m")

    # 피해 정보 확인
    print(f"\n💀 피해 정보:")
    print(f"  사망자: {items.get('deathCnt', 0)}명")
    print(f"  부상자: {items.get('injuryCnt', 0)}명")
    print(f"  차량: {items.get('vehicleCnt', 0)}대")

    # 지질 정보
    print(f"\n🪨 지질 정보: {items.get('grdKind', '정보없음')}")

    # 복구 정보
    print(f"\n🔧 복구 정보:")
    print(f"  상태: {items.get('trStatus', '정보없음')}")
    print(f"  방법: {items.get('trMethod', '정보없음')}")
    print(f"  완료일: {items.get('trFnDate', '정보없음')}")

    return {
        'has_dong_field': has_dong,
        'dong_value': dong,
        'has_size_info': bool(items.get('sinkWidth') or items.get('sinkDepth')),
        'has_damage_info': bool(items.get('deathCnt') is not None)
    }


def analyze_api7_evaluation_list():
    """API-7: 위험도평가 리스트 분석"""
    print("\n" + "="*80)
    print("📊 [API-7] 지반침하위험도평가 리스트 분석")
    print("="*80)

    data = load_json('API-7_evaluation_list.json')

    if not data:
        print("✗ 데이터 없음")
        return

    body = data.get('response', {}).get('body', {})
    total_count = body.get('totalCount', 0)
    items = body.get('items', {}).get('item', [])

    if isinstance(items, dict):
        items = [items]

    print(f"\n✅ 전체 데이터 건수: {total_count}건 (2023년 기준)")
    print(f"✅ 샘플 수집: {len(items)}건")

    # evalNm 샘플 수집 (파싱 테스트용)
    print(f"\n⚠️  평가명 (evalNm) 샘플 (위치 정보 추출 대상):")
    eval_names = []
    for idx, item in enumerate(items[:10], 1):
        eval_nm = item.get('evalNm', '')
        eval_names.append(eval_nm)
        print(f"  [{idx}] {eval_nm}")

    # evalNm 저장 (test_parsing.py에서 사용)
    eval_names_file = DATA_DIR / 'eval_names_sample.json'
    with open(eval_names_file, 'w', encoding='utf-8') as f:
        json.dump(eval_names, f, ensure_ascii=False, indent=2)
    print(f"\n✓ evalNm 샘플 저장: {eval_names_file}")

    return {
        'total_count': total_count,
        'sample_count': len(items),
        'eval_names': eval_names
    }


def analyze_api8_safety_measures():
    """API-8: 안전조치내용 분석"""
    print("\n" + "="*80)
    print("📊 [API-8] 안전조치내용 분석")
    print("="*80)

    data = load_json('API-8_safety_measures.json')

    if not data:
        print("✗ 데이터 없음")
        return

    body = data.get('response', {}).get('body', {})
    total_count = body.get('totalCount', 0)
    items = body.get('items', {}).get('item', [])

    if isinstance(items, dict):
        items = [items]

    print(f"\n✅ 총 안전조치 건수: {total_count}건")
    print(f"✅ 샘플 수집: {len(items)}건")

    if len(items) > 0:
        # 명령사유 분석 (위험도 추정 가능)
        reasons = [item.get('orderReason', '') for item in items]
        print(f"\n📋 명령사유 샘플:")
        for idx, reason in enumerate(reasons[:5], 1):
            print(f"  [{idx}] {reason}")

        # 조치 완료율
        completed = sum(1 for item in items if '완료' in item.get('actResult', ''))
        completion_rate = completed / len(items) * 100 if items else 0
        print(f"\n✅ 조치 완료율: {completion_rate:.1f}% ({completed}/{len(items)})")

    return {
        'total_count': total_count,
        'sample_count': len(items)
    }


def analyze_api9_emergency_measures():
    """API-9: 응급조치내용 분석"""
    print("\n" + "="*80)
    print("📊 [API-9] 응급조치내용 분석")
    print("="*80)

    data = load_json('API-9_emergency_measures.json')

    if not data:
        print("✗ 데이터 없음")
        return

    body = data.get('response', {}).get('body', {})
    total_count = body.get('totalCount', 0)
    items = body.get('items', {}).get('item', [])

    if isinstance(items, dict):
        items = [items]

    print(f"\n✅ 총 응급조치 건수: {total_count}건")
    print(f"✅ 샘플 수집: {len(items)}건")

    # API-8과 동일 여부 확인
    api8_data = load_json('API-8_safety_measures.json')
    if api8_data:
        api8_body = api8_data.get('response', {}).get('body', {})
        api8_items = api8_body.get('items', {}).get('item', [])
        if isinstance(api8_items, dict):
            api8_items = [api8_items]

        is_same = (json.dumps(items, sort_keys=True) == json.dumps(api8_items, sort_keys=True))
        print(f"\n⚠️  API-8과 동일 데이터 여부: {'YES' if is_same else 'NO'}")
        if is_same:
            print(f"  → API-8과 API-9는 동일한 endpoint 사용")
            print(f"  → orderReason 필드로 조치 유형 구분 필요")

    return {
        'total_count': total_count,
        'sample_count': len(items)
    }


def generate_summary_report(results: Dict):
    """종합 리포트 생성"""
    print("\n" + "🎯"*40)
    print("📊 SafeGround AI - 샘플 데이터 분석 종합 리포트")
    print("🎯"*40)

    # 전체 데이터 건수
    print("\n1️⃣ 전체 데이터 건수 (2023년 기준)")
    print("="*60)
    api12 = results.get('api12', {})
    api7 = results.get('api7', {})
    print(f"  API-12 (사고 리스트):       {api12.get('total_count', 0):>6,}건")
    print(f"  API-7  (위험도평가 리스트):  {api7.get('total_count', 0):>6,}건")

    # 핵심 확인 사항
    print("\n2️⃣ 핵심 확인 사항")
    print("="*60)
    api13 = results.get('api13', {})

    # dong 필드
    has_dong = api13.get('has_dong_field', False)
    print(f"  ✅ API-13 dong 필드:         {'✅ 존재!' if has_dong else '✗ 없음'}")
    if has_dong:
        print(f"     → 424개 행정동 매핑 가능!")
    else:
        print(f"     → evalNm 파싱 필요")

    # 데이터 품질
    print(f"\n  ✅ API-13 규모 정보:         {'✅ 있음' if api13.get('has_size_info') else '✗ 없음'}")
    print(f"  ✅ API-13 피해 정보:         {'✅ 있음' if api13.get('has_damage_info') else '✗ 없음'}")

    # 다음 단계
    print("\n3️⃣ 다음 단계 권장사항")
    print("="*60)

    if has_dong:
        print("  ✅ API-13으로 424개 행정동 매핑 가능")
        print("  ✅ 전체 데이터 수집 진행 권장")
        print("\n  📌 수집 전략:")
        print("     1. API-12 → 사고번호 리스트")
        print("     2. API-13 → 상세정보 (행정동, 규모, 피해)")
        print("     3. API-7  → 평가번호 리스트")
        print("     4. API-8/9 → 조치 정보")
    else:
        print("  ⚠️  evalNm 파싱 테스트 먼저 진행")
        print("  ⚠️  파싱 성공률 70% 이상 확인 후 전체 수집 결정")
        print("\n  📌 다음 작업:")
        print("     python test_parsing.py")

    # 예상 소요시간
    print("\n4️⃣ 전체 수집 예상 소요시간")
    print("="*60)
    total_accidents = api12.get('total_count', 0)
    total_evaluations = api7.get('total_count', 0)

    time_api12 = 5  # 초
    time_api13 = total_accidents * 0.5 / 60  # 분
    time_api7 = 5 / 60  # 분
    time_api89 = total_evaluations * 1 / 60  # 분 (API-8 + API-9)

    total_time = time_api12/60 + time_api13 + time_api7 + time_api89

    print(f"  API-12: ~5초")
    print(f"  API-13: ~{time_api13:.1f}분 ({total_accidents}건 × 0.5초)")
    print(f"  API-7:  ~5초")
    print(f"  API-8/9: ~{time_api89:.1f}분 ({total_evaluations}건 × 1초)")
    print(f"  총 예상시간: ~{total_time:.1f}분")


def main():
    """메인 실행 함수"""
    print("\n" + "🔍"*40)
    print("SafeGround AI - 샘플 데이터 분석")
    print("🔍"*40)

    results = {}

    # API-12 분석
    results['api12'] = analyze_api12_subsidence_list()

    # API-13 분석 (핵심!)
    results['api13'] = analyze_api13_subsidence_info()

    # API-7 분석
    results['api7'] = analyze_api7_evaluation_list()

    # API-8 분석
    results['api8'] = analyze_api8_safety_measures()

    # API-9 분석
    results['api9'] = analyze_api9_emergency_measures()

    # 종합 리포트
    generate_summary_report(results)

    print("\n" + "="*80)
    print("✅ 분석 완료!")
    print("="*80)


if __name__ == "__main__":
    main()
