from typing import List, Dict, Tuple, Optional
import heapq
import math

class Vertex:
    def __init__(self, id: int, lat: float, lng: float):
        self.id = id
        self.lat = lat
        self.lng = lng
        self.edges: Dict[int, float] = {}  # vertex_id -> weight
        self.visited = False
        self.distance = float('inf')
        self.previous = None

    def to_dict(self) -> dict:
        """JSON 직렬화를 위한 딕셔너리 변환"""
        return {
            'id': self.id,
            'lat': self.lat,
            'lng': self.lng,
            'visited': self.visited,
            'distance': str(self.distance) if self.distance == float('inf') else self.distance,
            'previous': self.previous
        }

class PathFinder:
    def __init__(self):
        self.vertices: Dict[int, Vertex] = {}
        self.visualization_steps = []
        self.current_step = 0

    def create_grid(self, start: Tuple[float, float], end: Tuple[float, float], density: int = 10) -> Tuple[int, int]:
        """시작점과 끝점 사이에 격자 형태의 정점들을 생성"""
        self.vertices.clear()
        self.visualization_steps.clear()
        
        start_lat, start_lng = start
        end_lat, end_lng = end
        
        # 격자 간격 계산
        lat_step = (end_lat - start_lat) / (density - 1)
        lng_step = (end_lng - start_lng) / (density - 1)
        
        # 정점 생성
        vertex_id = 0
        for i in range(density):
            for j in range(density):
                lat = start_lat + (lat_step * i)
                lng = start_lng + (lng_step * j)
                self.vertices[vertex_id] = Vertex(vertex_id, lat, lng)
                vertex_id += 1
        
        # 간선 생성 (8방향 연결)
        for i in range(density):
            for j in range(density):
                current_id = i * density + j
                
                # 8방향의 상대적 위치
                directions = [
                    (-1,-1), (-1,0), (-1,1),
                    (0,-1),          (0,1),
                    (1,-1),  (1,0),  (1,1)
                ]
                
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < density and 0 <= nj < density:
                        neighbor_id = ni * density + nj
                        distance = self.calculate_distance(
                            self.vertices[current_id],
                            self.vertices[neighbor_id]
                        )
                        self.vertices[current_id].edges[neighbor_id] = distance
        
        return 0, vertex_id - 1

    def calculate_distance(self, v1: Vertex, v2: Vertex) -> float:
        """두 정점 사이의 거리를 계산 (Haversine 공식 사용)"""
        R = 6371  # 지구의 반지름 (km)
        
        lat1, lon1 = math.radians(v1.lat), math.radians(v1.lng)
        lat2, lon2 = math.radians(v2.lat), math.radians(v2.lng)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

    def find_shortest_path(self, start_id: int, end_id: int) -> List[dict]:
        """다익스트라 알고리즘을 사용한 최단 경로 탐색"""
        # 초기화
        for vertex in self.vertices.values():
            vertex.visited = False
            vertex.distance = float('inf')
            vertex.previous = None
        
        self.vertices[start_id].distance = 0
        pq = [(0, start_id)]
        
        while pq:
            current_distance, current_id = heapq.heappop(pq)
            current_vertex = self.vertices[current_id]
            
            if current_vertex.visited:
                continue
                
            current_vertex.visited = True
            
            # 현재 상태 저장
            self.save_visualization_step(current_id)
            
            if current_id == end_id:
                break
            
            # 인접 정점 탐색
            for neighbor_id, weight in current_vertex.edges.items():
                neighbor = self.vertices[neighbor_id]
                if neighbor.visited:
                    continue
                    
                distance = current_vertex.distance + weight
                if distance < neighbor.distance:
                    neighbor.distance = distance
                    neighbor.previous = current_id
                    heapq.heappush(pq, (distance, neighbor_id))
        
        return self.visualization_steps

    def save_visualization_step(self, current_id: int) -> None:
        """현재 상태를 시각화 단계로 저장"""
        # 정점 상태
        vertices_state = {
            str(v.id): {
                'id': v.id,
                'lat': v.lat,
                'lng': v.lng,
                'visited': v.visited,
                'distance': str(v.distance) if v.distance == float('inf') else v.distance,
                'isCurrent': v.id == current_id,
                'style': {
                    'size': 8,
                    'color': '#e74c3c' if v.id == current_id else 
                            '#3498db' if v.visited else 
                            '#2ecc71' if v.distance < float('inf') else 
                            '#95a5a6',
                    'opacity': 1.0 if v.visited or v.id == current_id else 0.8
                }
            }
            for v in self.vertices.values()
        }
        
        # 간선 상태
        edges_state = []
        for v_id, vertex in self.vertices.items():
            for neighbor_id, weight in vertex.edges.items():
                if v_id < neighbor_id:  # 중복 방지
                    is_path = (vertex.previous == neighbor_id or 
                            self.vertices[neighbor_id].previous == v_id)
                    edges_state.append({
                        'from': v_id,
                        'to': neighbor_id,
                        'weight': weight,
                        'isPath': is_path,
                        'style': {
                            'width': 4 if is_path else 2,
                            'color': '#e74c3c' if is_path else '#bdc3c7',
                            'opacity': 0.8 if is_path else 0.5
                        }
                    })
        
        # 단계 저장
        step = {
            'vertices': vertices_state,
            'edges': edges_state,
            'currentId': current_id
        }
        self.visualization_steps.append(step)