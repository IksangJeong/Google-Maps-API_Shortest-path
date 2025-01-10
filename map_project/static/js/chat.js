// Socket.IO 연결 설정
const socket = io({
    transports: ['websocket'],
    pingTimeout: 30000,
    pingInterval: 25000
});

// 전역 변수
let currentRoom = '';
let myLocation = null;
let otherLocation = null;
let locationMarker = null;
let isSelectingLocation = false;
let userLocations = new Map();

// DOM 요소
const messagesContainer = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const usernameInput = document.getElementById('username');
const selectLocationBtn = document.getElementById('select-location');
const findMidpointBtn = document.getElementById('find-midpoint');

// 방 생성 버튼 이벤트
document.getElementById('create-room')?.addEventListener('click', async () => {
    const response = await fetch('/create-room', { method: 'POST' });
    const data = await response.json();
    window.location.href = `/join/${data.room_id}`;
});

// 방 참여 버튼 이벤트
document.getElementById('join-room')?.addEventListener('click', () => {
    const roomCode = document.getElementById('room-code').value.trim();
    if (roomCode) {
        window.location.href = `/join/${roomCode}`;
    } else {
        alert('방 코드를 입력하세요.');
    }
});

// 방 코드 복사 버튼 이벤트
document.getElementById('copy-room-id')?.addEventListener('click', () => {
    const roomId = document.getElementById('room-id').textContent;
    navigator.clipboard.writeText(roomId);
    alert('방 코드가 클립보드에 복사되었습니다.');
});

// 위치 선택 모드 토글
selectLocationBtn.addEventListener('click', () => {
    if (!isSelectingLocation) {
        isSelectingLocation = true;
        selectLocationBtn.innerHTML = '<span class="material-icons">close</span>선택 취소';
        selectLocationBtn.classList.add('selecting');
        window.map.setOptions({ draggableCursor: 'crosshair' });
    } else {
        isSelectingLocation = false;
        selectLocationBtn.innerHTML = '<span class="material-icons">add_location</span>내 위치 선택하기';
        selectLocationBtn.classList.remove('selecting');
        window.map.setOptions({ draggableCursor: null });
    }
});

// 지도 클릭 이벤트 핸들러
window.handleMapClick = (e) => {
    if (!isSelectingLocation) return;

    const clickedLocation = {
        lat: e.latLng.lat(),
        lng: e.latLng.lng()
    };

    // 이전 마커 제거
    if (locationMarker) {
        locationMarker.setMap(null);
    }

    // 새 마커 생성
    locationMarker = new google.maps.Marker({
        position: clickedLocation,
        map: window.map,
        label: {
            text: "내 위치",
            fontSize: "9px",
            color: "#FFFFFF",
            fontWeight: "bold",
        },
        title: "내 위치"
    });

    // 마커 클릭 이벤트 추가
    locationMarker.addListener('click', () => {
        if (confirm('이 핀을 삭제하시겠습니까?')) {
            locationMarker.setMap(null);
        }
    });

    // 위치 정보 저장
    myLocation = clickedLocation;
    // 선택한 위치의 주소 가져오기
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: clickedLocation }, (results, status) => {
        if (status === 'OK') {
            const address = results[0].formatted_address;
            
            // 위치 정보를 채팅으로 공유
            socket.emit('send_message', {
                username: usernameInput.value || '익명',
                type: 'location',
                location: clickedLocation,
                address: address,
                room: currentRoom,
                timestamp: new Date().toLocaleTimeString()
            });

            // 위치 선택 모드 종료
            isSelectingLocation = false;
            selectLocationBtn.innerHTML = '<span class="material-icons">add_location</span>내 위치 선택하기';
            selectLocationBtn.classList.remove('selecting');
            window.map.setOptions({ draggableCursor: null });
            
            displayMessage({
                username: 'System',
                message: `선택한 위치: ${address}`,
                timestamp: new Date().toLocaleTimeString()
            }, false, true);
        }
    });
};

// 메시지 전송 함수
function sendMessage() {
    const message = messageInput.value.trim();
    const username = usernameInput.value.trim() || '익명';

    if (message && currentRoom) {
        socket.emit('send_message', {
            username: username,
            message: message,
            room: currentRoom,
            timestamp: new Date().toLocaleTimeString()
        });
        messageInput.value = '';
    }
}

// 메시지 표시 함수
function displayMessage(data, isMine = false, isSystem = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = isSystem ? 'system-message' : 
                          `message ${isMine ? 'message-mine' : 'message-others'}`;

    const infoDiv = document.createElement('div');
    infoDiv.className = 'message-info';
    infoDiv.textContent = `${data.username} • ${data.timestamp}`;

    const contentDiv = document.createElement('div');
    contentDiv.textContent = data.message;

    messageDiv.appendChild(infoDiv);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // 스크롤을 최신 메시지로 이동
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 중간지점 찾기
findMidpointBtn.addEventListener('click', async () => {
    if (userLocations.size < 2) {
        alert('두 명 이상의 위치 정보가 필요합니다.');
        return;
    }

    try {
        // 모든 위치 쌍에 대해 중간지점 찾기
        const locations = Array.from(userLocations.values()).map(data => data.location);
        let allMidpoints = [];
        let totalDistance = 0;

        for (let i = 0; i < locations.length; i++) {
            for (let j = i + 1; j < locations.length; j++) {
                const response = await fetch("/find-midpoint", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        start: locations[i],
                        end: locations[j]
                    })
                });

                const data = await response.json();
                if (!data.error) {
                    allMidpoints.push(data.midpoint);
                    totalDistance += data.total_distance;

                    // 경로 표시
                    new google.maps.Polyline({
                        path: data.path,
                        geodesic: true,
                        strokeColor: "#FF0000",
                        strokeOpacity: 0.5,
                        strokeWeight: 2,
                        map: window.map
                    });
                }
            }
        }

        // 모든 중간지점의 평균 계산
        const centerPoint = {
            lat: allMidpoints.reduce((sum, point) => sum + point.lat, 0) / allMidpoints.length,
            lng: allMidpoints.reduce((sum, point) => sum + point.lng, 0) / allMidpoints.length
        };

        // 최종 중간지점 마커 표시
        const midpointMarker = new google.maps.Marker({
            position: centerPoint,
            map: window.map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: '#FF0000',
                fillOpacity: 0.8,
                strokeWeight: 2,
                strokeColor: '#FF0000'
            },
            title: '중간지점'
        });

        // 주변 장소 검색
        const service = new google.maps.places.PlacesService(window.map);
        service.nearbySearch({
            location: centerPoint,
            radius: 500,
            type: ['restaurant', 'cafe']
        }, (results, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                showPlaces(centerPoint, results);
            }
        });

        // 지도 중심 이동 및 줌
        window.map.setCenter(centerPoint);
        window.map.setZoom(15);

        // 거리 정보 표시
        displayMessage({
            username: 'System',
            message: `총 이동 거리: ${(totalDistance/1000).toFixed(2)}km`,
            timestamp: new Date().toLocaleTimeString()
        }, false, true);

    } catch (error) {
        console.error("Error:", error);
        alert("중간지점을 찾는 중 오류가 발생했습니다.");
    }
});

// 주변 장소 표시 함수
function showPlaces(center, places) {
    places.forEach(place => {
        // 장소 마커 생성
        new google.maps.Marker({
            position: place.geometry.location,
            map: window.map,
            title: place.name,
            icon: {
                url: place.icon,
                scaledSize: new google.maps.Size(24, 24)
            }
        });

        // 장소 정보 채팅으로 공유
        displayMessage({
            username: 'System',
            message: `주변 장소: ${place.name} (${place.vicinity})`,
            timestamp: new Date().toLocaleTimeString()
        }, false, true);
    });
}

// Socket.IO 이벤트 리스너
socket.on('connect', () => {
    console.log('서버에 연결되었습니다.');
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
});

// 채팅방 참여 처리
const roomId = document.getElementById('room-id')?.textContent;
if (roomId) {
    currentRoom = roomId;
    const joinRoom = () => {
        const username = usernameInput.value.trim();
        if (username) {
            socket.emit('join', { username, room: currentRoom });
            usernameInput.disabled = true;
        }
    };
    usernameInput.addEventListener('change', joinRoom);
    if (usernameInput.value.trim()) joinRoom();
}

socket.on('user_joined', (data) => {
    displayMessage({
        username: 'System',
        message: `${data.username}님이 입장하셨습니다.`,
        timestamp: new Date().toLocaleTimeString()
    }, false, true);
    updateUsersList(data.users);
});

socket.on('user_left', (data) => {
    displayMessage({
        username: 'System',
        message: `${data.username}님이 퇴장하셨습니다.`,
        timestamp: new Date().toLocaleTimeString()
    }, false, true);
    updateUsersList(data.users);
});

socket.on('room_status', (data) => {
    updateUsersList(data.users);
    
    // 기존 위치 정보 복원
    Object.entries(data.locations).forEach(([username, locationData]) => {
        userLocations.set(username, locationData);
        
        if (username !== usernameInput.value) {  // 내 위치는 제외
            new google.maps.Marker({
                position: locationData.location,
                map: window.map,
                label: username
            });
        }
    });

    // 중간지점 찾기 버튼 활성화 여부 결정
    findMidpointBtn.disabled = userLocations.size < 2;
});

socket.on('receive_message', (data) => {
    if (data.type === 'location') {
        userLocations.set(data.username, {
            location: data.location,
            address: data.address
        });

        if (data.username !== usernameInput.value) {
            new google.maps.Marker({
                position: data.location,
                map: window.map,
                label: data.username
            });
        }

        findMidpointBtn.disabled = userLocations.size < 2;

        displayMessage({
            username: 'System',
            message: `${data.username}님의 위치: ${data.address}`,
            timestamp: data.timestamp
        }, false, true);
    } else {
        displayMessage(data, data.username === usernameInput.value);
    }
});

// 이벤트 리스너
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// 참가자 목록 업데이트
function updateUsersList(users) {
    const container = document.getElementById('users-container');
    if (!container) return;
    
    container.innerHTML = users.map(user => `
        <div class="user-item">
            <span class="material-icons">person</span>
            ${user}
        </div>
    `).join('');
}