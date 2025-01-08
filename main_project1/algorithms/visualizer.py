from typing import Dict, List, Any
import json

class PathVisualizer:
    def __init__(self):
        self.visualization_steps: List[Dict[str, Any]] = []
        self.current_step = 0

    def add_step(self, step_data: Dict[str, Any]) -> None:
        """새로운 시각화 단계 추가"""
        self.visualization_steps.append(step_data)

    def get_vertex_style(self, vertex: Dict[str, Any]) -> Dict[str, Any]:
        """정점의 상태에 따른 스타일 반환"""
        style = {
            'size': 8,  # 기본 크기
            'color': '#95a5a6',  # 기본 색상 (회색)
            'opacity': 0.8,
        }
        
        if vertex['isCurrent']:
            style.update({
                'size': 12,
                'color': '#e74c3c',  # 현재 탐색 중인 정점 (빨간색)
                'opacity': 1,
            })
        elif vertex['visited']:
            style.update({
                'color': '#3498db',  # 방문한 정점 (파란색)
                'opacity': 1,
            })
        elif vertex['distance'] < float('inf'):
            style.update({
                'color': '#2ecc71',  # 발견했지만 아직 방문하지 않은 정점 (초록색)
            })
            
        return style

    def get_edge_style(self, edge: Dict[str, Any]) -> Dict[str, Any]:
        """간선의 상태에 따른 스타일 반환"""
        style = {
            'width': 2,  # 기본 두께
            'color': '#bdc3c7',  # 기본 색상 (연한 회색)
            'opacity': 0.5,
        }
        
        if edge['isPath']:
            style.update({
                'width': 4,
                'color': '#e74c3c',  # 현재 경로 (빨간색)
                'opacity': 0.8,
            })
            
        return style

    def get_current_step_data(self) -> Dict[str, Any]:
        """현재 단계의 시각화 데이터 반환"""
        if not self.visualization_steps:
            return {}
            
        step = self.visualization_steps[self.current_step]
        
        # 정점 스타일 적용
        vertices_with_style = {}
        for vid, vertex in step['vertices'].items():
            style = self.get_vertex_style(vertex)
            vertices_with_style[vid] = {**vertex, 'style': style}
        
        # 간선 스타일 적용
        edges_with_style = []
        for edge in step['edges']:
            style = self.get_edge_style(edge)
            edges_with_style.append({**edge, 'style': style})
        
        return {
            'vertices': vertices_with_style,
            'edges': edges_with_style,
            'currentId': step['currentId'],
            'stepNumber': self.current_step + 1,
            'totalSteps': len(self.visualization_steps)
        }

    def next_step(self) -> Dict[str, Any]:
        """다음 단계로 이동"""
        if self.current_step < len(self.visualization_steps) - 1:
            self.current_step += 1
        return self.get_current_step_data()

    def previous_step(self) -> Dict[str, Any]:
        """이전 단계로 이동"""
        if self.current_step > 0:
            self.current_step -= 1
        return self.get_current_step_data()

    def reset(self) -> None:
        """시각화 초기화"""
        self.current_step = 0
        self.visualization_steps = []

    def get_progress_info(self) -> Dict[str, Any]:
        """진행 상황 정보 반환"""
        if not self.visualization_steps:
            return {
                'currentStep': 0,
                'totalSteps': 0,
                'progress': 0
            }
            
        return {
            'currentStep': self.current_step + 1,
            'totalSteps': len(self.visualization_steps),
            'progress': (self.current_step + 1) / len(self.visualization_steps) * 100
        }

    def to_json(self) -> str:
        """시각화 데이터를 JSON 문자열로 변환"""
        return json.dumps(self.get_current_step_data())

    def get_step_description(self) -> str:
        """현재 단계에 대한 설명 생성"""
        if not self.visualization_steps:
            return "알고리즘이 시작되지 않았습니다."
            
        step = self.visualization_steps[self.current_step]
        current_vertex = step['vertices'][str(step['currentId'])]
        
        if current_vertex['isCurrent']:
            visited_count = sum(1 for v in step['vertices'].values() if v['visited'])
            remaining_count = len(step['vertices']) - visited_count
            
            return f"""현재 단계: {self.current_step + 1}/{len(self.visualization_steps)}
            탐색 중인 정점: {step['currentId']}
            방문한 정점: {visited_count}개
            남은 정점: {remaining_count}개
            현재까지의 거리: {current_vertex['distance']:.2f}km"""
            
        return "알고리즘이 완료되었습니다."