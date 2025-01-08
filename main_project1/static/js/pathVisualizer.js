class PathVisualizer {
    constructor(map) {
        this.map = map;
        this.markers = [];  // 정점 마커를 저장할 배열
        this.lines = [];    // 간선 라인을 저장할 배열
        this.currentStep = 0;
        this.steps = [];
        this.animationSpeed = 1000; // 1초
        this.isPlaying = false;

        // 컨트롤 버튼 초기화
        this.initializeControls();
    }

    initializeControls() {
        // 버튼 요소 가져오기
        this.prevButton = document.getElementById('prevStep');
        this.nextButton = document.getElementById('nextStep');
        this.resetButton = document.getElementById('reset');

        // 이벤트 리스너 등록
        this.prevButton.addEventListener('click', () => this.previousStep());
        this.nextButton.addEventListener('click', () => this.nextStep());
        this.resetButton.addEventListener('click', () => this.reset());
    }

    // 새로운 시각화 시작
    startVisualization(steps) {
        this.steps = steps;
        this.currentStep = 0;
        this.clearMap();
        this.updateControls();
        this.visualizeCurrentStep();
    }

    // 마커 생성 함수
    createMarker(position, style) {
        return new google.maps.Marker({
            position: position,
            map: this.map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: style.size || 8,
                fillColor: style.color || '#FF0000',
                fillOpacity: style.opacity || 0.8,
                strokeWeight: 1,
                strokeColor: style.color || '#FF0000',
            }
        });
    }

    // 라인 생성 함수
    createLine(from, to, style) {
        return new google.maps.Polyline({
            path: [from, to],
            strokeColor: style.color || '#FF0000',
            strokeOpacity: style.opacity || 1.0,
            strokeWeight: style.width || 2,
            map: this.map
        });
    }

    // 현재 단계 시각화
    visualizeCurrentStep() {
        const step = this.steps[this.currentStep];
        if (!step) return;

        this.clearMap();

        // 간선 그리기
        step.edges.forEach(edge => {
            if (!step.vertices[edge.from] || !step.vertices[edge.to]) return;
            
            const fromVertex = step.vertices[edge.from];
            const toVertex = step.vertices[edge.to];
            const fromPos = { lat: fromVertex.lat, lng: fromVertex.lng };
            const toPos = { lat: toVertex.lat, lng: toVertex.lng };

            const line = new google.maps.Polyline({
                path: [fromPos, toPos],
                strokeColor: edge.style.color,
                strokeOpacity: edge.style.opacity,
                strokeWeight: edge.style.width,
                map: this.map
            });
            
            this.lines.push(line);
        });

        // 정점 그리기
        Object.values(step.vertices).forEach(vertex => {
            const marker = new google.maps.Marker({
                position: { lat: vertex.lat, lng: vertex.lng },
                map: this.map,
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: vertex.style.size,
                    fillColor: vertex.style.color,
                    fillOpacity: vertex.style.opacity,
                    strokeWeight: 1,
                    strokeColor: vertex.style.color,
                }
            });
            
            this.markers.push(marker);
        });

        // 지도 범위 조정
        this.fitBounds();
        
        // 상태 정보 업데이트
        this.updateStatusInfo(step);
    }

    // 지도 범위 자동 조정
    fitBounds() {
        if (this.markers.length === 0) return;
        
        const bounds = new google.maps.LatLngBounds();
        this.markers.forEach(marker => {
            bounds.extend(marker.getPosition());
        });
        this.map.fitBounds(bounds);
    }

    // 맵 초기화
    clearMap() {
        // 마커 제거
        this.markers.forEach(marker => {
            if (marker) marker.setMap(null);
        });
        this.markers = [];

        // 라인 제거
        this.lines.forEach(line => {
            if (line) line.setMap(null);
        });
        this.lines = [];
    }

    // 상태 정보 업데이트
    updateStatusInfo(step) {
        const statusDiv = document.getElementById('algorithmStatus');
        const visitedCount = Object.values(step.vertices)
            .filter(v => v.visited).length;
        const totalCount = Object.keys(step.vertices).length;

        statusDiv.innerHTML = `
            <div class="status-info">
                <p><strong>진행 상태:</strong> ${this.currentStep + 1} / ${this.steps.length}</p>
                <p><strong>방문한 정점:</strong> ${visitedCount} / ${totalCount}</p>
                <p><strong>현재 정점:</strong> ${step.currentId}</p>
            </div>
        `;
    }

    // 다음 단계로 이동
    nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.currentStep++;
            this.visualizeCurrentStep();
            this.updateControls();
        }
    }

    // 이전 단계로 이동
    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.visualizeCurrentStep();
            this.updateControls();
        }
    }

    // 초기화
    reset() {
        this.currentStep = 0;
        this.clearMap();
        this.visualizeCurrentStep();
        this.updateControls();
        this.stopPlayback();
    }

    // 컨트롤 버튼 상태 업데이트
    updateControls() {
        this.prevButton.disabled = this.currentStep === 0;
        this.nextButton.disabled = this.currentStep === this.steps.length - 1;
        this.resetButton.disabled = this.currentStep === 0;
    }

    // 자동 재생 시작
    startPlayback() {
        if (!this.isPlaying) {
            this.isPlaying = true;
            this.playNextStep();
        }
    }

    // 자동 재생 정지
    stopPlayback() {
        this.isPlaying = false;
    }

    // 다음 단계 자동 재생
    playNextStep() {
        if (!this.isPlaying) return;

        if (this.currentStep < this.steps.length - 1) {
            this.nextStep();
            setTimeout(() => this.playNextStep(), this.animationSpeed);
        } else {
            this.isPlaying = false;
        }
    }

    // 애니메이션 속도 설정
    setAnimationSpeed(speed) {
        this.animationSpeed = speed;
    }
}

// 전역 변수로 PathVisualizer 인스턴스 저장
let pathVisualizer = null;

// 지도 로드 완료 후 PathVisualizer 초기화
function initializePathVisualizer(map) {
    console.log("Initializing PathVisualizer...");
    pathVisualizer = new PathVisualizer(map);
    console.log("PathVisualizer initialized:", pathVisualizer);
}