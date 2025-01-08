// 전역 변수 선언
let map;
let markers = [];
let startMarker = null;
let endMarker = null;

// 지도 초기화 함수
function initMap() {
    // 서울 시청을 중심으로 지도 초기화
    const defaultCenter = { lat: 37.5665, lng: 126.9780 };
    
    // 지도 객체 생성
    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultCenter,
        zoom: 14,
        styles: [
            {
                featureType: "poi",
                elementType: "labels",
                stylers: [{ visibility: "off" }],
            },
        ],
    });

    // Places Autocomplete 설정
    setupAutocomplete();

    // 이벤트 리스너 설정
    setupEventListeners();
}

// Places Autocomplete 설정
function setupAutocomplete() {
    const startInput = document.getElementById("start");
    const endInput = document.getElementById("end");

    const options = {
        componentRestrictions: { country: "kr" },
        fields: ["geometry", "name"],
    };

    const startAutocomplete = new google.maps.places.Autocomplete(startInput, options);
    const endAutocomplete = new google.maps.places.Autocomplete(endInput, options);

    // Autocomplete 선택 이벤트 처리
    startAutocomplete.addListener("place_changed", () => {
        const place = startAutocomplete.getPlace();
        if (place.geometry) {
            placeMarker(place.geometry.location, "start");
        }
    });

    endAutocomplete.addListener("place_changed", () => {
        const place = endAutocomplete.getPlace();
        if (place.geometry) {
            placeMarker(place.geometry.location, "end");
        }
    });
}

// 마커 생성/갱신 함수
function placeMarker(location, type) {
    // 기존 마커 제거
    if (type === "start" && startMarker) {
        startMarker.setMap(null);
    } else if (type === "end" && endMarker) {
        endMarker.setMap(null);
    }

    // 새 마커 생성
    const marker = new google.maps.Marker({
        position: location,
        map: map,
        title: type === "start" ? "출발지" : "도착지",
        label: type === "start" ? "S" : "E",
        animation: google.maps.Animation.DROP,
    });

    // 마커 저장
    if (type === "start") {
        startMarker = marker;
    } else {
        endMarker = marker;
    }

    // 지도 중심 이동
    map.panTo(location);

    // 두 지점이 모두 선택되었는지 확인
    checkBothLocationsSelected();
}

// 두 지점 선택 확인
function checkBothLocationsSelected() {
    const findPathButton = document.getElementById("findPath");
    if (startMarker && endMarker) {
        findPathButton.disabled = false;
    } else {
        findPathButton.disabled = true;
    }
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 경로 찾기 버튼 클릭 이벤트
    document.getElementById("findPath").addEventListener("click", () => {
        if (startMarker && endMarker) {
            startPathFinding(
                startMarker.getPosition().toJSON(),
                endMarker.getPosition().toJSON()
            );
        }
    });

    // 초기화 버튼 클릭 이벤트
    document.getElementById("reset").addEventListener("click", resetMap);
}

// 경로 찾기 시작
async function startPathFinding(start, end) {
    try {
        const response = await fetch("/api/path", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                start: start,
                end: end,
            }),
        });

        const data = await response.json();
        
        if (response.ok) {
            // TODO: PathVisualizer로 결과 전달
            console.log("경로 찾기 성공:", data);
        } else {
            showError(data.error || "경로를 찾을 수 없습니다.");
        }
    } catch (error) {
        showError("서버 오류가 발생했습니다.");
        console.error("Error:", error);
    }
}

// 지도 초기화
function resetMap() {
    // 마커 제거
    if (startMarker) startMarker.setMap(null);
    if (endMarker) endMarker.setMap(null);
    startMarker = null;
    endMarker = null;

    // 입력 필드 초기화
    document.getElementById("start").value = "";
    document.getElementById("end").value = "";

    // 버튼 상태 초기화
    document.getElementById("findPath").disabled = true;
    document.getElementById("prevStep").disabled = true;
    document.getElementById("nextStep").disabled = true;
    document.getElementById("reset").disabled = true;

    // TODO: PathVisualizer 초기화
}

// 에러 표시
function showError(message) {
    // TODO: 에러 메시지 표시 UI 구현
    alert(message);
}

// 페이지 로드시 지도 초기화
window.onload = initMap;