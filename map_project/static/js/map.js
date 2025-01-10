window.map = null;  // 전역으로 선언하여 다른 스크립트에서도 접근 가능하게 함
let startCoords, endCoords;
let pathPolylines = [];
let markers = [];
let currentVisualizationTimeout;
let pathData = null;
let animationSpeed = 100;

function initMap() {
    window.map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 37.5665, lng: 126.9780 }, // 서울 시청
        zoom: 13,
    });

    // 지도 클릭 이벤트 리스너 등록
    window.map.addListener('click', (e) => {
        if (window.handleMapClick) {
            window.handleMapClick(e);
        }
    });

    initializeAutocomplete();
    setupEventListeners();
}

function initializeAutocomplete() {
    const startInput = document.getElementById("start");
    const endInput = document.getElementById("end");

    const startAutocomplete = new google.maps.places.Autocomplete(startInput);
    const endAutocomplete = new google.maps.places.Autocomplete(endInput);

    startAutocomplete.addListener("place_changed", () => handlePlaceSelection(startAutocomplete, "S", "start"));
    endAutocomplete.addListener("place_changed", () => handlePlaceSelection(endAutocomplete, "E", "end"));
}

function handlePlaceSelection(autocomplete, label, type) {
    const place = autocomplete.getPlace();
    if (!place.geometry || !place.geometry.location) {
        alert(`유효한 ${type === "start" ? "출발지" : "도착지"} 주소를 입력하세요.`);
        return;
    }

    const coords = {
        lat: place.geometry.location.lat(),
        lng: place.geometry.location.lng(),
    };

    if (type === "start") startCoords = coords;
    else endCoords = coords;

    window.map.setCenter(coords);
    new google.maps.Marker({
        position: coords,
        map: window.map,
        label: label,
    });
}

function setupEventListeners() {
    document.getElementById("findPath").addEventListener("click", handleFindPath);
    document.getElementById("showPath").addEventListener("click", () => showFinalPath(true));
    document.getElementById("playVisualization").addEventListener("click", () => {
        animationSpeed = 100;
        clearVisualization();
        visualizeExplorationStep(pathData.exploredNodes);
    });
    document.getElementById("fastForward").addEventListener("click", () => {
        animationSpeed = 30;
        clearVisualization();
        visualizeExplorationStep(pathData.exploredNodes);
    });
    document.getElementById("instantShow").addEventListener("click", () => {
        showAllNodesInstantly();
    });
    document.getElementById("reset").addEventListener("click", clearVisualization);
}

async function handleFindPath() {
    if (!startCoords || !endCoords) {
        alert("출발지와 목적지를 모두 선택하세요.");
        return;
    }

    clearVisualization();
    document.getElementById("visualization-controls").classList.remove("hidden");

    try {
        const response = await fetch("/find-path", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ start: startCoords, end: endCoords }),
        });

        pathData = await response.json();

        if (pathData.error) {
            alert(pathData.error);
            return;
        }

        showFinalPath(true);
    } catch (error) {
        console.error("Error:", error);
        alert("경로를 찾는 중 오류가 발생했습니다.");
    }
}

function clearVisualization() {
    if (currentVisualizationTimeout) {
        clearTimeout(currentVisualizationTimeout);
    }
    markers.forEach(marker => marker.setMap(null));
    pathPolylines.forEach(line => line.setMap(null));
    markers = [];
    pathPolylines = [];
}

function createExplorationLine(from, to, isForward = true) {
    const line = new google.maps.Polyline({
        path: [
            { lat: from.lat, lng: from.lng },
            { lat: to.lat, lng: to.lng }
        ],
        geodesic: true,
        strokeColor: isForward ? "#4444FF" : "#44FF44",
        strokeOpacity: 0.4,
        strokeWeight: 2,
        map: window.map
    });
    pathPolylines.push(line);
    return line;
}

function visualizeExplorationStep(nodes, nodeIndex = 0) {
    if (!nodes || nodeIndex >= nodes.length) return;

    const node = nodes[nodeIndex];
    const isForward = node.direction === "forward";
    
    // 현재 노드 마커 생성
    const marker = new google.maps.Marker({
        position: { lat: node.lat, lng: node.lng },
        map: window.map,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 5,
            fillColor: isForward ? "#4444FF" : "#44FF44",
            fillOpacity: 0.7,
            strokeColor: isForward ? "#4444FF" : "#44FF44",
            strokeWeight: 1,
        },
    });
    markers.push(marker);

    // 비용 정보 표시
    const infoWindow = new google.maps.InfoWindow({
        content: `<div>Cost: ${node.cost.toFixed(2)}</div>`,
    });
    marker.addListener("click", () => {
        infoWindow.open(window.map, marker);
    });

    // 임시 최단 경로가 있다면 표시
    if (node.tempPath) {
        // 이전 임시 경로 제거
        pathPolylines.filter(line => line.tempPath).forEach(line => line.setMap(null));
        pathPolylines = pathPolylines.filter(line => !line.tempPath);
        
        // 새로운 임시 경로 표시
        const tempPathLine = new google.maps.Polyline({
            path: node.tempPath,
            geodesic: true,
            strokeColor: "#000000",
            strokeOpacity: 0.7,
            strokeWeight: 2,
            map: window.map
        });
        tempPathLine.tempPath = true;
        pathPolylines.push(tempPathLine);
    }

    // 이전 노드와 연결선 그리기
    if (node.previousNode !== null) {
        const previousNode = nodes.find(n => n.id === node.previousNode);
        if (previousNode) {
            createExplorationLine(
                { lat: previousNode.lat, lng: previousNode.lng },
                { lat: node.lat, lng: node.lng },
                isForward
            );
        }
    }

    // 다음 노드 처리
    currentVisualizationTimeout = setTimeout(() => {
        visualizeExplorationStep(nodes, nodeIndex + 1);
    }, animationSpeed);
}

function showFinalPath(showPath = true) {
    if (!pathData || !pathData.path) return;

    if (showPath) {
        const finalPath = new google.maps.Polyline({
            path: pathData.path,
            geodesic: true,
            strokeColor: "#FF0000",
            strokeOpacity: 1.0,
            strokeWeight: 3,
            map: window.map
        });
        pathPolylines.push(finalPath);
    }
}

function showAllNodesInstantly() {
    clearVisualization();
    
    // 최단 경로 먼저 표시
    showFinalPath(true);
    
    // 모든 노드와 연결선 즉시 표시
    pathData.exploredNodes.forEach(node => {
        const isForward = node.direction === "forward";
        
        // 노드 마커 생성
        const marker = new google.maps.Marker({
            position: { lat: node.lat, lng: node.lng },
            map: window.map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 5,
                fillColor: isForward ? "#4444FF" : "#44FF44",
                fillOpacity: 0.7,
                strokeColor: isForward ? "#4444FF" : "#44FF44",
                strokeWeight: 1,
            },
        });
        markers.push(marker);

        // 비용 정보 표시
        const infoWindow = new google.maps.InfoWindow({
            content: `<div>Cost: ${node.cost.toFixed(2)}</div>`,
        });
        marker.addListener("click", () => {
            infoWindow.open(window.map, marker);
        });

        // 이전 노드와 연결선 그리기
        if (node.previousNode !== null) {
            const previousNode = pathData.exploredNodes.find(n => n.id === node.previousNode);
            if (previousNode) {
                createExplorationLine(
                    { lat: previousNode.lat, lng: previousNode.lng },
                    { lat: node.lat, lng: node.lng },
                    isForward
                );
            }
        }
    });
}

window.onload = initMap;