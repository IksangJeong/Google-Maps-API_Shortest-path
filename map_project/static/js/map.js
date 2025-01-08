let map, startCoords, endCoords;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 37.7749, lng: -122.4194 }, // 초기 위치
        zoom: 13,
    });

    const startInput = document.getElementById("start");
    const endInput = document.getElementById("end");

    const startAutocomplete = new google.maps.places.Autocomplete(startInput);
    const endAutocomplete = new google.maps.places.Autocomplete(endInput);

    // 출발지 검색 이벤트
    startAutocomplete.addListener("place_changed", () => {
        const place = startAutocomplete.getPlace();
        if (!place.geometry || !place.geometry.location) {
            alert("유효한 출발지 주소를 입력하세요.");
            return;
        }
        startCoords = {
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng(),
        };
        map.setCenter(startCoords); // 지도 중심 이동
        new google.maps.Marker({
            position: startCoords,
            map: map,
            label: "S", // Start
        });
        alert("출발지가 설정되었습니다!");
    });

    // 도착지 검색 이벤트
    endAutocomplete.addListener("place_changed", () => {
        const place = endAutocomplete.getPlace();
        if (!place.geometry || !place.geometry.location) {
            alert("유효한 도착지 주소를 입력하세요.");
            return;
        }
        endCoords = {
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng(),
        };
        map.setCenter(endCoords); // 지도 중심 이동
        new google.maps.Marker({
            position: endCoords,
            map: map,
            label: "E", // End
        });
        alert("목적지가 설정되었습니다!");
    });
}

document.getElementById("findPath").addEventListener("click", async () => {
    if (!startCoords || !endCoords) {
        alert("출발지와 목적지를 모두 선택하세요.");
        return;
    }

    const response = await fetch("/find-path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start: startCoords, end: endCoords }),
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    const exploredNodes = data.exploredNodes;
    const shortestPath = data.path;

    // 탐색된 노드 시각화
    exploredNodes.forEach((node, index) => {
        setTimeout(() => {
            const marker = new google.maps.Marker({
                position: { lat: node.lat, lng: node.lng },
                map,
                label: `${index + 1}`,
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 5,
                    fillColor: "blue",
                    fillOpacity: 1,
                    strokeColor: "blue",
                    strokeWeight: 1,
                },
            });

            // 비용 정보 표시
            const infoWindow = new google.maps.InfoWindow({
                content: `<div>Cost: ${node.cost.toFixed(2)}</div>`,
            });
            marker.addListener("click", () => {
                infoWindow.open(map, marker);
            });
        }, index * 500); // 0.5초 간격으로 표시
    });

    // 최단 경로 시각화
    const pathCoordinates = shortestPath.map((coord) => new google.maps.LatLng(coord.lat, coord.lng));
    const pathPolyline = new google.maps.Polyline({
        path: pathCoordinates,
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 1.0,
        strokeWeight: 3,
    });
    pathPolyline.setMap(map);
});

window.onload = initMap;
