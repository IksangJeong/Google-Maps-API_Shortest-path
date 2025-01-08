let map, startMarker, endMarker;
let startCoords, endCoords;

function initMap() {
    // 지도 초기화
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 37.7749, lng: -122.4194 }, // 샌프란시스코 위치
        zoom: 13
    });

    // 출발지와 목적지 검색창에 Autocomplete 추가
    const startInput = document.getElementById("start");
    const endInput = document.getElementById("end");

    const startAutocomplete = new google.maps.places.Autocomplete(startInput);
    const endAutocomplete = new google.maps.places.Autocomplete(endInput);

    // 출발지 선택 시 지도에 마커 추가
    startAutocomplete.addListener("place_changed", () => {
        const place = startAutocomplete.getPlace();
        if (!place.geometry || !place.geometry.location) {
            alert("Invalid starting point");
            return;
        }
        startCoords = {
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng()
        };

        if (startMarker) startMarker.setMap(null);
        startMarker = new google.maps.Marker({
            position: startCoords,
            map: map,
            label: "S"
        });

        map.setCenter(startCoords);
    });

    // 목적지 선택 시 지도에 마커 추가
    endAutocomplete.addListener("place_changed", () => {
        const place = endAutocomplete.getPlace();
        if (!place.geometry || !place.geometry.location) {
            alert("Invalid destination");
            return;
        }
        endCoords = {
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng()
        };

        if (endMarker) endMarker.setMap(null);
        endMarker = new google.maps.Marker({
            position: endCoords,
            map: map,
            label: "E"
        });

        map.setCenter(endCoords);
    });
}

// 경로 요청
document.getElementById('findPath').addEventListener('click', async () => {
    if (!startCoords || !endCoords) {
        alert("Please select both starting point and destination.");
        return;
    }

    const response = await fetch('/find-path', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start: startCoords, end: endCoords })
    });
    const data = await response.json();
    console.log("Shortest Path:", data.path);

    // 결과를 지도에 표시
    if (data.path) {
        const pathCoordinates = data.path.map(coord => new google.maps.LatLng(coord.lat, coord.lng));
        const pathPolyline = new google.maps.Polyline({
            path: pathCoordinates,
            geodesic: true,
            strokeColor: "#FF0000",
            strokeOpacity: 1.0,
            strokeWeight: 2
        });
        pathPolyline.setMap(map);
    } else {
        alert("Failed to find a route.");
    }
});

window.onload = initMap;
