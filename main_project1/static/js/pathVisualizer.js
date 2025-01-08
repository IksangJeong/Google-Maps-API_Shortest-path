class PathVisualizer {
    constructor(map) {
        this.map = map;
        this.markers = [];
        this.lines = [];
        this.currentStep = 0;
        this.steps = [];
        this.isPlaying = false;
    }

    // 새로운 시각화 시작
    startVisualization(steps) {
        this.steps = steps;
        this.currentStep = 0;
        this.clearMap();
        this.visualizeCurrentStep();
    }

    // 현재 단계 시각화
    visualizeCurrentStep() {
        const step = this.steps[this.currentStep];
        if (!step) return;

        this.clearMap();

        // 경로 그리기 (path 사용)
        if (step.path) {
            const coordinates = step.path.map(coord => ({
                lat: coord[0] / 1e6, // 좌표 변환
                lng: coord[1] / 1e6  // 좌표 변환
            }));

            const line = new google.maps.Polyline({
                path: coordinates,
                strokeColor: "#0000FF", // 경로 색상
                strokeOpacity: 0.8,
                strokeWeight: 4,
                map: this.map,
            });

            this.lines.push(line);

            // 경로의 시작점과 끝점을 표시
            new google.maps.Marker({
                position: coordinates[0], // 시작점
                map: this.map,
                label: "S",
            });

            new google.maps.Marker({
                position: coordinates[coordinates.length - 1], // 끝점
                map: this.map,
                label: "E",
            });
        }

        // 지도 범위 조정
        this.fitBounds();
    }

    // 지도 범위 자동 조정
    fitBounds() {
        if (this.lines.length === 0) return;

        const bounds = new google.maps.LatLngBounds();

        this.lines.forEach(line => {
            line.getPath().forEach(latlng => {
                bounds.extend(latlng);
            });
        });

        this.map.fitBounds(bounds);
    }

    // 맵 초기화
    clearMap() {
        this.lines.forEach(line => {
            if (line) line.setMap(null);
        });
        this.lines = [];
    }

    reset() {
        this.currentStep = 0;
        this.clearMap();
    }
}

// 전역 변수로 PathVisualizer 인스턴스 저장
let pathVisualizer = null;

// 지도 로드 완료 후 PathVisualizer 초기화
function initializePathVisualizer(map) {
    pathVisualizer = new PathVisualizer(map);
}