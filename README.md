# SafeGround AI - 싱크홀 위험도 예측 프로젝트

서울시 427개 행정동의 싱크홀 위험도를 예측하는 AI 프로젝트

## 프로젝트 목표

- **대상 지역**: 서울시 427개 행정동
- **분석 기간**: 120개월 (10년)
- **데이터 소스**: 공공데이터포털 API 5개
- **최종 목표**: 행정동별 싱크홀 위험도 예측 모델

## 현재 진행 상황

### ✅ Week 2: 데이터 탐색 완료 (2026-01-01)

공공데이터포털 API 5개를 탐색하여 데이터 구조 파악 완료:

- **API-12**: 지반침하사고 리스트 조회 (156건/년)
- **API-13**: 지반침하사고 상세정보 조회 ⭐ **dong 필드 제공!**
- **API-7**: 지반침하위험도평가 리스트 조회 (245건/년)
- **API-8**: 안전조치내용 조회
- **API-9**: 응급조치내용 조회

**핵심 발견사항**:
- ✅ API-13에서 **행정동(dong) 필드 제공** → 424개 행정동 매핑 가능
- ✅ evalNm 파싱 성공률 **80%** (목표 70% 초과)
- ✅ 전체 데이터 수집 진행 권장

자세한 내용: [EXPLORATION_REPORT.md](./EXPLORATION_REPORT.md)

## 프로젝트 구조

```
sinkhole/
├── data/
│   ├── seoul_424dong.csv              # 서울시 424개 행정동 정보
│   └── sample/                        # API 샘플 데이터
├── explore_apis.py                    # Step 1: API 샘플링
├── analyze_sample.py                  # Step 2: 샘플 분석
├── test_parsing.py                    # Step 3: evalNm 파싱 테스트
├── EXPLORATION_REPORT.md              # 데이터 탐색 리포트
└── README.md                          # 본 파일
```

## 사용 방법

### 0. API 인증키 설정 (최초 1회)

`explore_apis.py` 파일을 열어서 API 키를 입력하세요:

```python
# 🔑 API 인증키 설정
SERVICE_KEY_DECODED = "여기에_디코딩_키_입력"  # 일반 인증키 (추천)
SERVICE_KEY_ENCODED = "여기에_인코딩_키_입력"  # URL 인코딩된 키
USE_DECODED_KEY = True  # 디코딩 키 사용 (True 권장)
```

**어디서 키를 확인하나요?**
1. https://www.data.go.kr 로그인
2. 마이페이지 → 오픈API → 활용신청 현황
3. "지반침하위험도평가" 서비스 찾기
4. 인증키(디코딩), 인증키(인코딩) 복사

### 1. API 샘플링

```bash
python3 explore_apis.py
```

5개 API에서 10건씩 샘플 데이터 수집 (실제 공공데이터)

### 2. 샘플 분석

```bash
python3 analyze_sample.py
```

샘플 데이터 구조 분석 및 통계 출력

### 3. evalNm 파싱 테스트

```bash
python3 test_parsing.py
```

위치 정보 추출 성공률 테스트 (목표: 70% 이상)

## 다음 단계

- [ ] 전체 데이터 수집 스크립트 작성 (collect_all_data.py)
- [ ] PostgreSQL DB 설계 및 저장
- [ ] Feature Engineering (행정동별 사고 이력, 위험도평가)
- [ ] 예측 모델 학습

## API 인증키

공공데이터포털에서 발급받은 인증키 사용:
- 서비스명: 지반침하위험도평가 및 사고정보 조회 서비스
- 제공기관: 국토교통부

## 기술 스택

- Python 3.x
- requests (API 호출)
- pandas (데이터 분석)
- PostgreSQL (데이터 저장)

## 라이선스

MIT License

## 작성자

SafeGround AI Team
