class PathVisualizer {
    constructor(map) {
        this.map = map;
        this.markers = new Map();  // 정점 마커 저장
        this.lines = new Map();    // 간선 라인 저장
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
                scale: style.size,
                fillColor: style.color,
                fillOpacity: style.opacity,
                strokeWeight: 1,
                strokeColor: style.color,
            }
        });
    }

    // 라인 생성 함수
    createLine(from, to, style) {
        return new google.maps.Polyline({
            path: [from, to],
            strokeColor: style.color,
            strokeOpacity: style.opacity,
            strokeWeight: style.width,
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
            const fromVertex = step.vertices[edge.from];
            const toVertex = step.vertices[edge.to];
            const fromPos = { lat: fromVertex.lat, lng: fromVertex.lng };
            const toPos = { lat: toVertex.lat, lng: toVertex.lng };

            const line = this.createLine(fromPos, toPos, edge.style);
            this.lines.set(`${edge.from}-${edge.to}`, line);
        });

        // 정점 그리기
        Object.values(step.vertices).forEach(vertex => {
            const position = { lat: vertex.lat, lng: vertex.lng };
            const marker = this.createMarker(position, vertex.style);
            this.markers.set(vertex.id, marker);
        });

        // 상태 정보 업데이트
        this.updateStatusInfo(step);
    }

    // 상태 정보 업데이트
    updateStatusInfo(step) {
        const statusDiv = document.getElementById('algorithmStatus');
        const visitedCount = Object.values(step.vertices)
            .filter(v => v.visited).length;
        const totalCount = Object.keys(step.vertices).length;

        statusDiv.innerHTML = `
            <p>단계: ${this.currentStep + 1} / ${this.steps.length}</p>
            <p>방문한 정점: ${visitedCount} / ${totalCount}</p>
            <p>현재 정점: ${step.currentId}</p>
        `;
    }

    // 맵 초기화
    clearMap() {
        this.markers.forEach(marker => marker.setMap(null));
        this.lines.forEach(line => line.setMap(null));
        this.markers.clear();
        this.lines.clear();
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
    pathVisualizer = new PathVisualizer(map);
}