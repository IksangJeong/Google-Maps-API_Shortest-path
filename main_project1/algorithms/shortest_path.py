import osmnx as ox
import networkx as nx
from typing import List, Dict, Tuple
import math
from shapely.geometry import Point, LineString
import numpy as np

class RoadNetwork:
    def __init__(self):
        self.graph = None
        self.nodes = {}
        self.edges = {}
        self.visualization_steps = []

    def load_network(self, center_lat: float, center_lng: float, radius: int = 2000):
        """주어진 중심점 주변의 도로 네트워크 로드"""
        try:
            # OpenStreetMap에서 도로 네트워크 다운로드
            print(f"Loading road network for coordinates: {center_lat}, {center_lng}")
            
            # 이미 단순화된 그래프 가져오기
            self.graph = ox.graph_from_point(
                center_point=(center_lat, center_lng),
                dist=radius,
                network_type='drive',
                simplify=True  # 처음부터 단순화된 그래프 요청
            )
            
            # 그래프를 프로젝션된 그래프로 변환 (미터 단위 사용)
            self.graph = ox.project_graph(self.graph)
            
            # 노드와 엣지 정보 업데이트
            self.nodes = {node: data for node, data in self.graph.nodes(data=True)}
            self.edges = {(u, v): data for u, v, data in self.graph.edges(data=True)}
            
            print(f"Network loaded successfully with {len(self.nodes)} nodes and {len(self.edges)} edges")
            
        except Exception as e:
            print(f"Error loading network: {str(e)}")
            raise

    def find_nearest_node(self, lat: float, lng: float, exclude_nodes=None) -> int:
        """주어진 좌표에서 가장 가까운 노드 찾기"""
        try:
            if exclude_nodes is None:
                exclude_nodes = set()
                
            # 모든 노드와의 거리 계산
            distances = {}
            for node_id, node_data in self.nodes.items():
                if node_id in exclude_nodes:
                    continue
                    
                node_lat = node_data['y']
                node_lng = node_data['x']
                distance = self._haversine_distance(lat, lng, node_lat, node_lng)
                distances[node_id] = distance
                
            # 가장 가까운 노드 찾기
            nearest_node = min(distances.items(), key=lambda x: x[1])
            node_id, distance = nearest_node
            
            print(f"Found nearest node {node_id} at distance {distance:.2f}m")
            return node_id
            
        except Exception as e:
            print(f"Error finding nearest node: {str(e)}")
            raise

    def find_path(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> List[Dict]:
        """두 지점 간의 최단 경로 찾기"""
        try:
            print(f"Finding path from ({start_lat}, {start_lng}) to ({end_lat}, {end_lng})")
            
            # 가장 가까운 노드 찾기
            start_node = self.find_nearest_node(start_lat, start_lng)
            # 시작점을 제외한 가장 가까운 노드 찾기
            end_node = self.find_nearest_node(end_lat, end_lng, {start_node})
            
            print(f"Selected nodes - Start: {start_node}, End: {end_node}")
            
            # 경로 찾기 시작
            self.visualization_steps = []
            
            try:
                # A* 알고리즘으로 경로 찾기
                path_nodes = nx.astar_path(
                    self.graph,
                    start_node,
                    end_node,
                    weight='length',
                    heuristic=self._distance_heuristic
                )
                
                print(f"Path found with {len(path_nodes)} nodes")
                
                # 경로의 각 단계 저장
                path_coords = []
                for i in range(len(path_nodes) - 1):
                    current = path_nodes[i]
                    next_node = path_nodes[i + 1]
                    
                    # 엣지 데이터 가져오기
                    edge_data = self.graph.get_edge_data(current, next_node)[0]
                    
                    # 경로 포인트 추출
                    if 'geometry' in edge_data:
                        # 도로의 실제 형태 사용
                        coords = list(edge_data['geometry'].coords)
                        path_coords.extend(coords)
                    else:
                        # 직선으로 연결
                        start_coord = (self.nodes[current]['y'], self.nodes[current]['x'])
                        end_coord = (self.nodes[next_node]['y'], self.nodes[next_node]['x'])
                        path_coords.extend([start_coord, end_coord])
                    
                    # 시각화 단계 저장
                    self._save_step(path_nodes, i, path_coords)
                
                print(f"Visualization steps created: {len(self.visualization_steps)}")
                return self.visualization_steps
                
            except nx.NetworkXNoPath:
                print("No path found between the points")
                return []
                
        except Exception as e:
            print(f"Error in find_path: {str(e)}")
            raise
            
            try:
                # A* 알고리즘으로 경로 찾기
                path_nodes = nx.astar_path(
                    self.graph,
                    start_node,
                    end_node,
                    weight='length',
                    heuristic=self._distance_heuristic
                )
                
                print(f"Path found with {len(path_nodes)} nodes")
                
                # 경로의 각 단계 저장
                path_coords = []
                for i in range(len(path_nodes) - 1):
                    current = path_nodes[i]
                    next_node = path_nodes[i + 1]
                    
                    # 엣지 데이터 가져오기
                    edge_data = self.graph.get_edge_data(current, next_node)[0]
                    
                    # 경로 포인트 추출
                    if 'geometry' in edge_data:
                        # 도로의 실제 형태 사용
                        coords = list(edge_data['geometry'].coords)
                        path_coords.extend(coords)
                    else:
                        # 직선으로 연결
                        start_coord = (self.nodes[current]['y'], self.nodes[current]['x'])
                        end_coord = (self.nodes[next_node]['y'], self.nodes[next_node]['x'])
                        path_coords.extend([start_coord, end_coord])
                    
                    # 시각화 단계 저장
                    self._save_step(path_nodes, i, path_coords)
                
                print(f"Visualization steps created: {len(self.visualization_steps)}")
                return self.visualization_steps
                
            except nx.NetworkXNoPath:
                print("No path found between the points")
                return []
                
        except Exception as e:
            print(f"Error in find_path: {str(e)}")
            raise

    def _distance_heuristic(self, u: int, v: int) -> float:
        """A* 알고리즘을 위한 휴리스틱 함수"""
        try:
            u_lat = self.nodes[u]['y']
            u_lng = self.nodes[u]['x']
            v_lat = self.nodes[v]['y']
            v_lng = self.nodes[v]['x']
            
            return self._haversine_distance(u_lat, u_lng, v_lat, v_lng)
        except Exception as e:
            print(f"Error in heuristic calculation: {str(e)}")
            return 0

    def _haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """두 지점 간의 Haversine 거리 계산"""
        R = 6371  # 지구의 반지름 (km)
        
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c * 1000  # 미터 단위로 변환

    def _save_step(self, path_nodes: List[int], current_index: int, current_path: List[Tuple[float, float]]):
        """현재 경로 탐색 단계 저장"""
        try:
            current_node = path_nodes[current_index]
            
            # 노드 상태
            nodes_state = {}
            for node_id in self.nodes:
                node_data = self.nodes[node_id]
                is_in_path = node_id in path_nodes[:current_index + 1]
                is_current = node_id == current_node
                
                nodes_state[str(node_id)] = {
                    'id': node_id,
                    'lat': float(node_data['y']),
                    'lng': float(node_data['x']),
                    'visited': is_in_path,
                    'isCurrent': is_current,
                    'style': {
                        'size': 8 if is_current else 6,
                        'color': '#e74c3c' if is_current else '#3498db' if is_in_path else '#95a5a6',
                        'opacity': 1.0 if is_in_path or is_current else 0.6
                    }
                }
            
            # 엣지 상태
            edges_state = []
            visited_edges = set()
            
            for i in range(current_index):
                u, v = path_nodes[i], path_nodes[i + 1]
                edge_key = (min(u, v), max(u, v))
                
                if edge_key not in visited_edges:
                    edge_data = self.graph.get_edge_data(u, v)[0]
                    
                    edge = {
                        'from': str(u),
                        'to': str(v),
                        'weight': float(edge_data.get('length', 0)),
                        'isPath': True,
                        'style': {
                            'width': 4,
                            'color': '#e74c3c',
                            'opacity': 0.8
                        }
                    }
                    
                    if 'geometry' in edge_data:
                        coords = list(edge_data['geometry'].coords)
                        edge['geometry'] = [(float(x), float(y)) for x, y in coords]
                    
                    edges_state.append(edge)
                    visited_edges.add(edge_key)
            
            step_data = {
                'vertices': nodes_state,
                'edges': edges_state,
                'currentId': str(current_node),
                'path': [(float(lat), float(lng)) for lat, lng in current_path]
            }
            
            self.visualization_steps.append(step_data)
            
        except Exception as e:
            print(f"Error saving visualization step: {str(e)}")
            raise