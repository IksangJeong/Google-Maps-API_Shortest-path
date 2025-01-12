# 실시간 위치 공유 및 중간지점 찾기 서비스 🗺️

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=Flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-010101?style=flat-square&logo=Socket.io&logoColor=white)](https://socket.io/)
[![Google Maps](https://img.shields.io/badge/Google_Maps-4285F4?style=flat-square&logo=Google-Maps&logoColor=white)](https://developers.google.com/maps)

## 📌 프로젝트 소개

실시간으로 여러 사용자의 위치를 공유하고, A* 알고리즘을 활용하여 최적의 중간지점을 찾아주는 웹 서비스입니다.
<img width="1389" alt="스크린샷 2025-01-10 오전 10 30 32" src="https://github.com/user-attachments/assets/adef1e7a-87f7-4ee3-bce1-9336c31f7d88" />
<img width="1389" alt="스크린샷 2025-01-10 오전 10 31 04" src="https://github.com/user-attachments/assets/6186fcb8-7ceb-4523-8fb9-c9d6143ab535" /><img width="1389" alt="스크린샷 2025-01-10 오전 10 31 12" src="https://github.com/user-attachments/assets/974138e1-203c-4a37-8f3e-b1a73b741c4c" />

<img width="1389" alt="스크린샷 2025-01-10 오전 10 31 12" src="https://github.com/user-attachments/assets/2766a145-eca2-4135-b988-f1816c414ec5" />
<img width="1389" alt="스크린샷 2025-01-10 오전 10 32 33" src="https://github.com/user-attachments/assets/bf202c57-5d5b-4e76-9ff7-53bc10c256a6" /><img width="1389" alt="스크린샷 2025-01-10 오전 10 32 33" src="https://github.com/user-attachments/assets/19a48d74-0900-4b7a-8cb7-eb0a7a13eb34" />
<img width="1389" alt="스크린샷 2025-01-10 오전 10 30 43" src="https://github.com/user-attachments/assets/2bcac9bc-3390-4245-a628-f13452ac54a5" />

<img width="1389" alt="스크린샷 2025-01-10 오전 10 30 55" src="https://github.com/user-attachments/assets/b2fef254-05f3-469c-9c7c-6ab03a46d876" />


<<<<<<< HEAD
### ✨ 주요 기능
- 실시간 채팅방 생성 및 참여
- 지도에서 클릭으로 위치 선택 및 공유
- A* 알고리즘 기반 최단 경로 탐색
- 다중 사용자 간 최적 중간지점 계산
- 중간지점 주변 음식점/카페 추천

## 🛠️ 기술 스택
=======
## ✨ 주요 기능
- 🔍 Google Maps 기반 경로 탐색
- 🚗 양방향 A* 알고리즘 구현
- 📊 경로 탐색 과정 단계별 시각화
- 💬 실시간 채팅 및 위치 공유, 중간 지점 찾기

## 왜 이 프로젝트인가?
알고리즘이 길을 찾는 과정은 복잡하고 때로는 혼란스러울 수 있습니다. 이 프로젝트는 사용자가 경로 탐색의 과정을 직관적이고 시각적으로 이해할 수 있도록 돕습니다. 알고리즘의 작동 방식을 실시간으로 보여주어 경로 탐색의 마법을 이해할 수 있습니다.
>>>>>>> f8468fc0d581c79ab9fcc5d9a19a4331f5862f36

### Frontend
- HTML5, CSS3, JavaScript
- Google Maps JavaScript API
- Socket.IO Client

<<<<<<< HEAD
### Backend
- Python
=======
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

- map_project 폴더를 엽니다.

### 필수 요구사항
- Python 3.8+
>>>>>>> f8468fc0d581c79ab9fcc5d9a19a4331f5862f36
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

<<<<<<< HEAD
- **직관적인 UI/UX**
  - 드래그 & 드롭 방식의 위치 선택
  - 실시간 시각적 피드백
  - 반응형 디자인
=======
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
                <img src="![23B22D5A-DC9E-4BFD-B766-03E99E92304B](https://github.com/user-attachments/assets/d6ef0978-da8f-4845-9c64-11e5a9c51cb0)" width="100" height="100">
                <br>
                <a href="#">정익상</a>
                <br>
                경로 알고리즘 개발
            </td>
          

</table>
</div>
>>>>>>> f8468fc0d581c79ab9fcc5d9a19a4331f5862f36

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

<<<<<<< HEAD
💡 문의사항이나 제안사항이 있으시다면 Issues에 남겨주세요!
=======
본 프로젝트는 지속적으로 업데이트되고 개선될 예정입니다.
>>>>>>> f8468fc0d581c79ab9fcc5d9a19a4331f5862f36
