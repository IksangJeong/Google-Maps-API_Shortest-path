# 실시간 위치 공유 및 중간지점 찾기 서비스 🗺️

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=Flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-010101?style=flat-square&logo=Socket.io&logoColor=white)](https://socket.io/)
[![Google Maps](https://img.shields.io/badge/Google_Maps-4285F4?style=flat-square&logo=Google-Maps&logoColor=white)](https://developers.google.com/maps)

## 📌 프로젝트 소개

실시간으로 여러 사용자의 위치를 공유하고, A* 알고리즘을 활용하여 최적의 중간지점을 찾아주는 웹 서비스입니다.

### ✨ 주요 기능
- 실시간 채팅방 생성 및 참여
- 지도에서 클릭으로 위치 선택 및 공유
- A* 알고리즘 기반 최단 경로 탐색
- 다중 사용자 간 최적 중간지점 계산
- 중간지점 주변 음식점/카페 추천

## 🛠️ 기술 스택

### Frontend
- HTML5, CSS3, JavaScript
- Google Maps JavaScript API
- Socket.IO Client

### Backend
- Python
- Flask
- Flask-SocketIO
- OSMnx (도로 네트워크 데이터)

## 💻 실행 방법

1. 저장소 클론
```bash
git clone [repository-url]
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
```bash
# .env 파일 생성
GOOGLE_MAPS_API_KEY=your_api_key_here
```

4. 서버 실행
```bash
python app.py
```

## 🎯 사용 방법

1. **방 생성/참여**
   - '방 만들기' 버튼으로 새로운 방 생성
   - 생성된 방 코드를 공유하여 다른 사용자 초대
   - 방 코드 입력으로 기존 방 참여

2. **위치 공유**
   - '내 위치 선택하기' 클릭
   - 지도에서 원하는 위치 클릭
   - 자동으로 다른 참여자들과 위치 공유

3. **중간지점 찾기**
   - 2명 이상의 위치가 공유되면 활성화
   - 모든 참여자의 최적 중간지점 계산
   - 주변 추천 장소 자동 표시

## 🌟 주요 특징

- **실시간 상호작용**
  - WebSocket을 통한 실시간 채팅
  - 실시간 위치 정보 업데이트
  - 참여자 목록 실시간 동기화

- **스마트한 경로 탐색**
  - A* 알고리즘 기반 최단 경로 계산
  - 실제 도로 네트워크 기반 분석
  - 다중 사용자 최적 중간지점 계산

- **직관적인 UI/UX**
  - 드래그 & 드롭 방식의 위치 선택
  - 실시간 시각적 피드백
  - 반응형 디자인

## 📱 스크린샷

[스크린샷 이미지들 추가 예정]

## 🔒 라이센스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👥 Contributors

[프로필 이미지 및 링크 추가 예정]

---

💡 문의사항이나 제안사항이 있으시다면 Issues에 남겨주세요!