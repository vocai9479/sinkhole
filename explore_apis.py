#!/usr/bin/env python3
"""
SafeGround AI - 공공데이터 API 탐색 스크립트

목표: 5개 API에서 10건씩 샘플링하여 데이터 구조 파악
- API-12: 지반침하사고 리스트 조회
- API-13: 지반침하사고 상세정보 조회
- API-7: 지반침하위험도평가 리스트 조회
- API-8: 안전조치내용 조회
- API-9: 응급조치내용 조회
"""

import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# API 설정
BASE_URL = "http://apis.data.go.kr/1611000/undergroundsafetyinfo01"

# ============================================================================
# 🔑 API 인증키 설정 (공공데이터포털에서 발급받은 키 입력)
# ============================================================================
# 통합 일반 인증키 (최근 공공데이터포털 방식)
SERVICE_KEY = "여기에_일반_인증키_입력"

# 참고: 공공데이터포털 마이페이지 → 오픈API → 활용신청 현황에서 확인
# ============================================================================

# 데이터 저장 경로
DATA_DIR = Path("data/sample")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_json(data: Dict, filename: str):
    """JSON 파일 저장"""
    filepath = DATA_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ 저장 완료: {filepath}")


def api_request(endpoint: str, params: Dict, description: str = "") -> Optional[Dict]:
    """
    공통 API 요청 함수

    Args:
        endpoint: API endpoint
        params: 요청 파라미터
        description: 설명 (로그용)

    Returns:
        API 응답 딕셔너리 또는 None (실패 시)
    """
    from urllib.parse import urlencode, unquote

    url = f"{BASE_URL}/{endpoint}"
    params['serviceKey'] = SERVICE_KEY
    params['type'] = 'json'

    print(f"\n{'='*60}")
    print(f"📡 API 호출: {description}")
    print(f"Endpoint: {endpoint}")
    print(f"Params: {params}")

    try:
        # URL 빌드 (serviceKey는 인코딩하지 않음)
        query_params = {k: v for k, v in params.items() if k != 'serviceKey'}
        query_string = urlencode(query_params)
        full_url = f"{url}?{query_string}&serviceKey={unquote(SERVICE_KEY)}"

        print(f"Full URL (처음 100자): {full_url[:100]}...")

        response = requests.get(full_url, timeout=30)

        # 에러 응답 상세 확인
        if response.status_code != 200:
            print(f"✗ HTTP 에러: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None

        data = response.json()

        # 결과 코드 확인
        header = data.get('response', {}).get('header', {})
        result_code = header.get('resultCode')
        result_msg = header.get('resultMsg')

        print(f"Result Code: {result_code}")
        print(f"Result Msg: {result_msg}")

        if result_code == '00' or result_code == '0':
            body = data.get('response', {}).get('body', {})
            total_count = body.get('totalCount', 0)
            print(f"✓ 성공: 총 {total_count}건")
            return data
        else:
            print(f"✗ 실패: {result_msg}")
            return None

    except Exception as e:
        print(f"✗ 오류: {e}")
        return None


def explore_api12_subsidence_list() -> Optional[List[Dict]]:
    """
    API-12: 지반침하사고 리스트 조회
    최근 1년 데이터 10건 샘플링
    """
    print("\n" + "="*80)
    print("🔍 [API-12] 지반침하사고 리스트 조회")
    print("="*80)

    # 최근 1년 (2023년) 데이터
    params = {
        'sagoDateFrom': '20230101',
        'sagoDateTo': '20231231',
        'pageNo': 1,
        'numOfRows': 10
    }

    result = api_request(
        'getSubsidenceList01',
        params,
        "사고 리스트 (2023년, 10건)"
    )

    if result:
        save_json(result, 'API-12_subsidence_list.json')

        # 아이템 추출
        body = result.get('response', {}).get('body', {})
        items = body.get('items', {}).get('item', [])

        if isinstance(items, dict):
            items = [items]

        print(f"\n📊 샘플 데이터 미리보기:")
        for idx, item in enumerate(items[:3], 1):
            print(f"  [{idx}] 사고번호: {item.get('sagoNo')}")
            print(f"      위치: {item.get('siDo')} {item.get('siGunGu')}")
            print(f"      일자: {item.get('sagoDate')}")
            print(f"      원인: {item.get('sagoDetail', '확정중')}")

        return items

    return None


def explore_api13_subsidence_info(sago_no: str) -> Optional[Dict]:
    """
    API-13: 지반침하사고 상세정보 조회

    Args:
        sago_no: 사고번호 (API-12에서 획득)
    """
    print("\n" + "="*80)
    print("🔍 [API-13] 지반침하사고 상세정보 조회")
    print("="*80)

    params = {
        'sagoNo': sago_no,
        'pageNo': 1,
        'numOfRows': 10
    }

    result = api_request(
        'getSubsidenceInfo01',
        params,
        f"사고 상세정보 (사고번호: {sago_no})"
    )

    if result:
        save_json(result, 'API-13_subsidence_info.json')

        # 상세정보 미리보기
        body = result.get('response', {}).get('body', {})
        items = body.get('items', {}).get('item', {})

        if isinstance(items, list):
            items = items[0] if items else {}

        print(f"\n📊 상세 정보 미리보기:")
        print(f"  사고번호: {items.get('sagoNo')}")
        print(f"  ⭐ 행정동: {items.get('dong')} (424개 행정동 매핑 핵심!)")
        print(f"  상세주소: {items.get('addr')}")
        print(f"  규모 - 폭: {items.get('sinkWidth')}m, 깊이: {items.get('sinkDepth')}m")
        print(f"  지질: {items.get('grdKind')}")
        print(f"  사망자: {items.get('deathCnt')}명, 부상자: {items.get('injuryCnt')}명")
        print(f"  복구상태: {items.get('trStatus')}")

        return items

    return None


def explore_api7_evaluation_list() -> Optional[List[Dict]]:
    """
    API-7: 지반침하위험도평가 리스트 조회
    최근 1년 데이터 10건 샘플링
    """
    print("\n" + "="*80)
    print("🔍 [API-7] 지반침하위험도평가 리스트 조회")
    print("="*80)

    # 최근 1년 (2023년) 데이터
    params = {
        'startYmd': '20230101',
        'endYmd': '20231231',
        'pageNo': 1,
        'numOfRows': 10
    }

    result = api_request(
        'getSubsidenceEvaluationList01',
        params,
        "위험도평가 리스트 (2023년, 10건)"
    )

    if result:
        save_json(result, 'API-7_evaluation_list.json')

        # 아이템 추출
        body = result.get('response', {}).get('body', {})
        items = body.get('items', {}).get('item', [])

        if isinstance(items, dict):
            items = [items]

        print(f"\n📊 샘플 데이터 미리보기:")
        for idx, item in enumerate(items[:3], 1):
            print(f"  [{idx}] 평가번호: {item.get('evalNo')}")
            print(f"      ⚠️  평가명: {item.get('evalNm')} (위치 정보 파싱 필요!)")

        return items

    return None


def explore_api8_safety_measures(eval_no: str) -> Optional[Dict]:
    """
    API-8: 안전조치내용 조회

    Args:
        eval_no: 평가번호 (API-7에서 획득)
    """
    print("\n" + "="*80)
    print("🔍 [API-8] 안전조치내용 조회")
    print("="*80)

    params = {
        'evalNo': eval_no,
        'pageNo': 1,
        'numOfRows': 10
    }

    result = api_request(
        'getSubsidenceResult01',
        params,
        f"안전조치 내용 (평가번호: {eval_no})"
    )

    if result:
        save_json(result, 'API-8_safety_measures.json')

        # 상세정보 미리보기
        body = result.get('response', {}).get('body', {})
        items = body.get('items', {}).get('item', [])

        if isinstance(items, dict):
            items = [items]

        print(f"\n📊 안전조치 정보 미리보기 ({len(items)}건):")
        for idx, item in enumerate(items[:3], 1):
            print(f"  [{idx}] 명령일자: {item.get('orderDate')}")
            print(f"      명령사유: {item.get('orderReason')}")
            print(f"      조치방법: {item.get('actMethod')}")
            print(f"      조치기한: {item.get('actLimitYmd')}")

        return items

    return None


def explore_api9_emergency_measures(eval_no: str) -> Optional[Dict]:
    """
    API-9: 응급조치내용 조회

    Args:
        eval_no: 평가번호 (API-7에서 획득)
    """
    print("\n" + "="*80)
    print("🔍 [API-9] 응급조치내용 조회")
    print("="*80)

    params = {
        'evalNo': eval_no,
        'pageNo': 1,
        'numOfRows': 10
    }

    # API-9는 getSubsidenceExpediency01 사용 (API-8과 다름!)
    result = api_request(
        'getSubsidenceExpediency01',
        params,
        f"응급조치 내용 (평가번호: {eval_no})"
    )

    if result:
        save_json(result, 'API-9_emergency_measures.json')

        # 상세정보 미리보기
        body = result.get('response', {}).get('body', {})
        items = body.get('items', {}).get('item', [])

        if isinstance(items, dict):
            items = [items]

        print(f"\n📊 응급조치 정보 미리보기 ({len(items)}건):")
        for idx, item in enumerate(items[:3], 1):
            print(f"  [{idx}] 명령일자: {item.get('orderDate')}")
            print(f"      명령사유: {item.get('orderReason')}")
            print(f"      조치결과: {item.get('actResult')}")

        return items

    return None


def main():
    """메인 실행 함수"""
    print("\n" + "🚀"*40)
    print("SafeGround AI - 공공데이터 API 긴급 탐색")
    print("목표: 5개 API에서 10건씩 샘플링 → 구조 파악 → 전체 수집 여부 결정")
    print("🚀"*40)

    start_time = time.time()

    # Step 1: API-12 - 사고 리스트 조회
    accidents = explore_api12_subsidence_list()
    time.sleep(1)  # Rate limiting

    # Step 2: API-13 - 사고 상세정보 조회 (API-12의 첫 번째 사고번호 사용)
    if accidents and len(accidents) > 0:
        sago_no = accidents[0].get('sagoNo')
        if sago_no:
            explore_api13_subsidence_info(sago_no)
            time.sleep(1)

    # Step 3: API-7 - 위험도평가 리스트 조회
    evaluations = explore_api7_evaluation_list()
    time.sleep(1)

    # Step 4 & 5: API-8, API-9 - 안전조치/응급조치 조회 (API-7의 첫 번째 평가번호 사용)
    if evaluations and len(evaluations) > 0:
        eval_no = evaluations[0].get('evalNo')
        if eval_no:
            explore_api8_safety_measures(eval_no)
            time.sleep(1)
            explore_api9_emergency_measures(eval_no)

    # 완료 메시지
    elapsed = time.time() - start_time
    print("\n" + "="*80)
    print(f"✅ 탐색 완료! 소요시간: {elapsed:.1f}초")
    print(f"📁 데이터 저장 위치: {DATA_DIR.absolute()}")
    print("="*80)

    # 다음 단계 안내
    print("\n📌 다음 단계:")
    print("  1. python analyze_sample.py  - 샘플 데이터 분석")
    print("  2. python test_parsing.py    - evalNm 파싱 테스트")
    print("  3. 전체 데이터 수집 여부 결정")


if __name__ == "__main__":
    main()
