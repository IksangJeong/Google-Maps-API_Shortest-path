// 전역 변수 선언
let map;
let markers = [];
let polyline;
let geocoder;

// 페이지 로드시 지도 초기화
window.onload = function() {
    initMap();
};

// 지도 초기화 함수
function initMap() {
    // Google Maps 초기화
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 37.5665, lng: 126.9780 }, // 서울시청 좌표
        zoom: 14
    });

    // Geocoder 초기화
    geocoder = new google.maps.Geocoder();

    // Places Autocomplete 설정
    const originInput = document.getElementById('origin');
    const destinationInput = document.getElementById('destination');
    
    // Autocomplete 옵션 설정
    const options = {
        componentRestrictions: { country: 'kr' }, // 한국 내 결과로 제한
        fields: ['formatted_address', 'geometry', 'name'],
        strictBounds: false
    };
    
    // Autocomplete 객체 생성
    const originAutocomplete = new google.maps.places.Autocomplete(originInput, options);
    const destinationAutocomplete = new google.maps.places.Autocomplete(destinationInput, options);
    
    // Autocomplete 선택 이벤트 리스너
    originAutocomplete.addListener('place_changed', function() {
        const place = originAutocomplete.getPlace();
        if (place.geometry) {
            addMarker(place.geometry.location, '출발');
            if (markers.length === 2) findRouteFromMarkers();
        }
    });
    
    destinationAutocomplete.addListener('place_changed', function() {
        const place = destinationAutocomplete.getPlace();
        if (place.geometry) {
            addMarker(place.geometry.location, '도착');
            if (markers.length === 2) findRouteFromMarkers();
        }
    });

    // 검색 버튼에 이벤트 리스너 추가
    document.getElementById('findRouteBtn').addEventListener('click', () => {
        const origin = document.getElementById('origin').value;
        const destination = document.getElementById('destination').value;
        
        if (origin && destination) {
            geocodeAddresses(origin, destination);
        } else {
            showError('출발지와 도착지를 모두 입력해주세요.');
        }
    });
}

// 마커로부터 경로 찾기
function findRouteFromMarkers() {
    if (markers.length !== 2) return;
    
    const origin = markers[0].getPosition();
    const destination = markers[1].getPosition();
    findRoute(origin, destination);
}

// 주소를 좌표로 변환하는 함수
function geocodeAddresses(origin, destination) {
    clearMarkers(); // 기존 마커 제거

    // 출발지 좌표 변환
    geocoder.geocode({ address: origin }, (results1, status1) => {
        if (status1 === 'OK') {
            const originLocation = results1[0].geometry.location;
            
            // 도착지 좌표 변환
            geocoder.geocode({ address: destination }, (results2, status2) => {
                if (status2 === 'OK') {
                    const destinationLocation = results2[0].geometry.location;
                    
                    // 마커 생성
                    addMarker(originLocation, '출발');
                    addMarker(destinationLocation, '도착');
                    
                    // 경로 찾기 호출
                    findRoute(originLocation, destinationLocation);
                } else {
                    showError('도착지 주소를 찾을 수 없습니다.');
                }
            });
        } else {
            showError('출발지 주소를 찾을 수 없습니다.');
        }
    });
}

// 마커 추가 함수
function addMarker(location, label) {
    // 출발/도착 마커는 하나씩만 유지
    if (label === '출발' && markers[0]) {
        markers[0].setMap(null);
        markers[0] = null;
    } else if (label === '도착' && markers[1]) {
        markers[1].setMap(null);
        markers[1] = null;
    }

    const marker = new google.maps.Marker({
        position: location,
        map: map,
        label: label
    });
    
    if (label === '출발') {
        markers[0] = marker;
    } else {
        markers[1] = marker;
    }
}

// 마커 제거 함수
function clearMarkers() {
    markers.forEach(marker => {
        if (marker) marker.setMap(null);
    });
    markers = [];
    if (polyline) {
        polyline.setMap(null);
    }
}

// 경로 찾기 함수
async function findRoute(origin, destination) {
    try {
        // 같은 위치 체크
        if (origin.lat() === destination.lat() && 
            origin.lng() === destination.lng()) {
            showError('출발지와 도착지가 같습니다. 다른 위치를 선택해주세요.');
            return;
        }

        const response = await fetch('/api/route', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                origin: {
                    lat: origin.lat(),
                    lng: origin.lng()
                },
                destination: {
                    lat: destination.lat(),
                    lng: destination.lng()
                }
            })
        });

        const data = await response.json();

        if (data.success) {
            displayRoute(data);
            // 지도 범위 조정
            const bounds = new google.maps.LatLngBounds();
            markers.forEach(marker => {
                if (marker) bounds.extend(marker.getPosition());
            });
            map.fitBounds(bounds);
        } else {
            showError(data.error || '경로를 찾을 수 없습니다.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('경로 검색 중 오류가 발생했습니다.');
    }
}

// 경로 표시 함수
function displayRoute(routeData) {
    // 기존 경로 삭제
    if (polyline) {
        polyline.setMap(null);
    }

    // 경로 좌표 생성
    const path = routeData.path.map(coord => new google.maps.LatLng(coord.lat, coord.lng));

    // 새로운 경로 그리기
    polyline = new google.maps.Polyline({
        path: path,
        strokeColor: '#FF0000',
        strokeOpacity: 1.0,
        strokeWeight: 2
    });

    polyline.setMap(map);

    // 경로 정보 표시
    const routeInfo = document.getElementById('routeInfo');
    routeInfo.innerHTML = `
        <h3>경로 정보</h3>
        <p>총 거리: ${routeData.total_distance}</p>
    `;
}

// 에러 표시 함수
function showError(message) {
    const modal = document.getElementById('errorModal');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    modal.style.display = 'block';

    // 모달 닫기 버튼
    const closeBtn = document.getElementsByClassName('close')[0];
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    };

    // 모달 외부 클릭시 닫기
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };
}