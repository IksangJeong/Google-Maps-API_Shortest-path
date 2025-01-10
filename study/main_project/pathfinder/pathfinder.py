from typing import List, Dict, Tuple
import heapq
import math
from .models import Coordinate, Node

class PathFinder:
    def __init__(self):
        self.nodes: Dict[int, Node] = {}
        self.grid_size = 0.005  # 약 500m 간격

    def create_road_network(self, start: Coordinate, end: Coordinate):
        """도로망 생성"""
        self.nodes.clear()
        
        # 시작점과 끝점 추가
        start_id = self.add_node(start, "start")
        end_id = self.add_node(end, "end")
        
        # 경로 상의 중간 지점들 생성
        lat_diff = (end.lat - start.lat) / 10
        lng_diff = (end.lng - start.lng) / 10
        
        # 중간 지점 생성 (9개의 중간점)
        for i in range(1, 10):
            lat = start.lat + lat_diff * i
            lng = start.lng + lng_diff * i
            self.add_node(Coordinate(lat, lng), "waypoint")
            
        # 모든 노드를 서로 연결
        nodes = list(self.nodes.keys())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                node1, node2 = nodes[i], nodes[j]
                distance = self.calculate_distance(
                    self.nodes[node1].coord,
                    self.nodes[node2].coord
                )
                self.add_connection(node1, node2, distance)
        
        return start_id, end_id

    def add_node(self, coord: Coordinate, node_type: str) -> int:
        """새로운 노드 추가"""
        node_id = len(self.nodes)
        self.nodes[node_id] = Node(node_id, coord, {}, node_type)
        return node_id

    def add_connection(self, from_id: int, to_id: int, distance: float):
        """노드 간 연결 추가"""
        self.nodes[from_id].connections[to_id] = distance
        self.nodes[to_id].connections[from_id] = distance

    def calculate_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        """두 좌표 간의 거리 계산"""
        R = 6371  # 지구의 반지름 (km)
        
        lat1, lon1 = math.radians(coord1.lat), math.radians(coord1.lng)
        lat2, lon2 = math.radians(coord2.lat), math.radians(coord2.lng)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

    def find_shortest_path(self, start_id: int, goal_id: int) -> Tuple[List[Coordinate], float]:
        """Dijkstra 알고리즘을 사용한 최단 경로 탐색"""
        if start_id not in self.nodes or goal_id not in self.nodes:
            return [], float('inf')
        
        # 거리 초기화
        distances = {node: float('inf') for node in self.nodes}
        distances[start_id] = 0
        
        # 이전 노드 추적
        previous = {node: None for node in self.nodes}
        
        # 우선순위 큐 초기화
        pq = [(0, start_id)]
        
        # 방문한 노드 집합
        visited = set()
        
        while pq:
            current_distance, current_id = heapq.heappop(pq)
            
            if current_id in visited:
                continue
                
            visited.add(current_id)
            
            if current_id == goal_id:
                break
                
            # 이웃 노드 검사
            for neighbor_id, weight in self.nodes[current_id].connections.items():
                if neighbor_id in visited:
                    continue
                    
                distance = current_distance + weight
                
                if distance < distances[neighbor_id]:
                    distances[neighbor_id] = distance
                    previous[neighbor_id] = current_id
                    heapq.heappush(pq, (distance, neighbor_id))
        
        # 경로가 없는 경우
        if distances[goal_id] == float('inf'):
            return [], float('inf')
            
        # 경로 재구성
        path = []
        current_id = goal_id
        
        while current_id is not None:
            path.append(self.nodes[current_id].coord)
            current_id = previous[current_id]
            
        path.reverse()
        
        return path, distances[goal_id]

    def get_path_details(self, path: List[Coordinate]) -> Dict:
        """경로 세부 정보 계산"""
        if not path:
            return {
                "total_distance": 0,
                "segments": []
            }
            
        total_distance = 0
        segments = []
        
        for i in range(len(path) - 1):
            distance = self.calculate_distance(path[i], path[i+1])
            total_distance += distance
            
            segments.append({
                "start": path[i],
                "end": path[i+1],
                "distance": distance
            })
        
        return {
            "total_distance": total_distance,
            "segments": segments
        }