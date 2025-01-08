async function initMap() {
    // 지도 초기화
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 7,
        center: { lat: 36.444117, lng: 127.119045 }, // 중심을 대한민국 중부로 설정
    });

    // Flask에서 장소 데이터 가져오기
    const response = await fetch('/locations');
    const locations = await response.json();

    // 마커와 경로 그리기
    const markers = [];
    const path = [];

    locations.forEach(location => {
        const position = { lat: location.lat, lng: location.lng };

        // 마커 추가
        const marker = new google.maps.Marker({
            position,
            map,
            title: location.name,
        });

        markers.push(marker);
        path.push(position);
    });

    // 경로 그리기
    const route = new google.maps.Polyline({
        path,
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 1.0,
        strokeWeight: 2,
    });

    route.setMap(map);
}

// 지도 초기화
window.onload = initMap;