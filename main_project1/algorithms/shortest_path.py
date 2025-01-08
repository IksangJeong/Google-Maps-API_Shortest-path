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

class PathFinder:
    def __init__(self):
        self.vertices: Dict[int, Vertex] = {}
        self.visualization_steps = []
        self.current_step = 0

    def create_grid(self, start: Tuple[float, float], end: Tuple[float, float], density: int = 10):
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
        
        return 0, vertex_id - 1  # 시작점과 끝점의 vertex_id 반환

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

    def find_shortest_path(self, start_id: int, end_id: int) -> List[Dict]:
        """다익스트라 알고리즘을 사용한 최단 경로 탐색"""
        # 초기화
        for vertex in self.vertices.values():
            vertex.visited = False
            vertex.distance = float('inf')
            vertex.previous = None
        
        self.vertices[start_id].distance = 0
        pq = [(0, start_id)]
        self.visualization_steps = []
        
        while pq:
            current_distance, current_id = heapq.heappop(pq)
            current_vertex = self.vertices[current_id]
            
            if current_vertex.visited:
                continue
                
            current_vertex.visited = True
            
            # 현재 상태 저장
            self.save_step(current_id)
            
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

    def save_step(self, current_id: int):
        """현재 상태를 시각화 단계로 저장"""
        vertices_state = {}
        edges_state = []
        
        # 정점 상태 저장
        for vertex_id, vertex in self.vertices.items():
            vertices_state[vertex_id] = {
                'id': vertex_id,
                'lat': vertex.lat,
                'lng': vertex.lng,
                'visited': vertex.visited,
                'distance': vertex.distance,
                'isCurrent': vertex_id == current_id
            }
        
        # 간선 상태 저장
        for vertex_id, vertex in self.vertices.items():
            for neighbor_id, weight in vertex.edges.items():
                if vertex_id < neighbor_id:  # 중복 방지
                    edges_state.append({
                        'from': vertex_id,
                        'to': neighbor_id,
                        'weight': weight,
                        'isPath': self.is_edge_in_current_path(vertex_id, neighbor_id)
                    })
        
        self.visualization_steps.append({
            'vertices': vertices_state,
            'edges': edges_state,
            'currentId': current_id
        })

    def is_edge_in_current_path(self, v1_id: int, v2_id: int) -> bool:
        """현재 찾은 경로에 해당 간선이 포함되어 있는지 확인"""
        for vertex_id in self.vertices:
            vertex = self.vertices[vertex_id]
            if vertex.previous is not None:
                if (vertex_id == v1_id and vertex.previous == v2_id) or \
                   (vertex_id == v2_id and vertex.previous == v1_id):
                    return True
        return False