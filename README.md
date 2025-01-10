# 🗺️ 경로 탐색 시각화 프로젝트

<h2 align="center">언제 어디서든 함께 길을 찾아요!</h2>

<div align="center">
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=flask&logoColor=white">
  <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
  <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white">
  <img src="https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white">
  <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white">
</div>

## 🌟 프로젝트 소개
이 프로젝트는 A* 알고리즘을 사용하여 도로 네트워크에서 최단 경로를 찾고 탐색 과정을 시각적으로 보여주는 웹 애플리케이션입니다.

## ✨ 주요 기능
- 🔍 Google Maps 기반 경로 탐색
- 🚗 양방향 A* 알고리즘 구현
- 📊 경로 탐색 과정 단계별 시각화
- 💬 실시간 채팅 및 위치 공유 기능

## 왜 이 프로젝트인가?
길을 찾는 과정은 복잡하고 때로는 혼란스러울 수 있습니다. 우리 프로젝트는 사용자가 경로 탐색의 과정을 직관적이고 시각적으로 이해할 수 있도록 돕습니다. 알고리즘의 작동 방식을 실시간으로 보여주어 경로 탐색의 마법을 이해할 수 있습니다.

## 🛠 기술 스택
- Backend: Flask, Python
- Frontend: JavaScript, HTML, CSS
- Map API: Google Maps
- Real-time Communication: Socket.IO
- Routing Algorithm: A* Search

## 🚀 주요 기능 상세

### 경로 탐색 알고리즘
- 양방향 A* 알고리즘 구현
- OSMnx를 사용한 도로 네트워크 그래프 로드
- 노드 간 최단 경로 탐색

### 시각화 기능
- 경로 탐색 과정의 단계별 애니메이션
- 탐색된 노드와 최종 경로 시각화
- 다양한 재생 속도 지원 (일반, 고속)

### 채팅 및 위치 공유
- 실시간 채팅 
- 사용자 위치 선택 및 공유
- 참가자들의 중간 지점 찾기 기능

## 📦 설치 및 실행

### 필수 요구사항
- Python 3.8+
- Flask
- OSMnx
- Google Maps API Key

### 설치 단계
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # 윈도우의 경우 venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (.env 파일)
GOOGLE_MAPS_API_KEY=your_api_key

# 서버 실행
python app.py
```

## 🤝 기여 방법

### 브랜치 전략
```
main
└── develop
    ├── feature/routing
    ├── feature/visualization
    └── feature/chat
```

### 커밋 메시지 규칙
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 작업
- `refactor`: 코드 리팩토링
- `test`: 테스트 코드 추가
- `chore`: 기타 작업

### 커밋 예시
```
feat: Add bidirectional A* search visualization
fix: Resolve graph loading error in path finder
docs: Update README with installation instructions
```

## 🔍 향후 계획
- 더 많은 지역의 도로 네트워크 지원
- 다양한 경로 탐색 알고리즘 추가
- 성능 최적화
- 모바일 반응형 디자인 개선

## 📬 추가 개발 계획
- 다양한 교통수단 경로 지원
- 실시간 교통 상황 반영
- 경로 공유 및 저장 기능
- 사용자 맞춤형 경로 추천

## 📝 라이선스
MIT License

## 👥 개발자
<div align='center'>
<table>
    <thead>
        <tr>
            <th colspan="3">프로젝트 개발자</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td align='center'>
                <img src="https://via.placeholder.com/100" width="100" height="100">
                <br>
                <a href="#">정익상</a>
                <br>
                경로 알고리즘 개발
            </td>
          
        </tr>
    </tbody>
</table>
</div>

## 🐛 버그 제보 및 기여
Issues and Pull Requests are welcome!

## 📌 주의사항
- Google Maps API Key가 필요합니다
- 일부 기능은 인터넷 연결이 필요합니다

---

본 프로젝트는 지속적으로 업데이트되고 개선될 예정입니다.
