import osmnx as ox
import heapq
import math

def haversine(lat1, lon1, lat2, lon2):
    """두 지점 간의 대원 거리 계산 (단위: m)."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def prepare_graph(graph):
    """그래프 데이터를 노드와 엣지로 변환."""
    nodes, edges = ox.graph_to_gdfs(graph)
    node_positions = {node: (data["y"], data["x"]) for node, data in graph.nodes(data=True)}
    adjacency_list = {}

    for u, v, data in graph.edges(data=True):
        distance = data.get("length", 1)
        if u not in adjacency_list:
            adjacency_list[u] = []
        adjacency_list[u].append((v, distance))

    return node_positions, adjacency_list

def get_closest_node(lat, lon, node_positions):
    """주어진 좌표에서 가장 가까운 노드를 찾는다."""
    closest_node = None
    closest_distance = float("inf")

    for node, (n_lat, n_lon) in node_positions.items():
        distance = haversine(lat, lon, n_lat, n_lon)
        if distance < closest_distance:
            closest_node = node
            closest_distance = distance

    return closest_node

def a_star_search(start, goal, node_positions, adjacency_list):
    """A* 알고리즘으로 최단 경로 탐색."""
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored_nodes = []

    while frontier:
        _, current = heapq.heappop(frontier)
        explored_nodes.append(current)

        if current == goal:
            break

        for neighbor, cost in adjacency_list.get(current, []):
            new_cost = cost_so_far[current] + cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + haversine(
                    node_positions[neighbor][0], node_positions[neighbor][1],
                    node_positions[goal][0], node_positions[goal][1]
                )
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()

    return path, explored_nodes

def bidirectional_a_star(start, goal, node_positions, adjacency_list):
    """양방향 A* 알고리즘으로 최단 경로 탐색."""
    frontier_start = [(0, start)]
    frontier_goal = [(0, goal)]
    came_from_start = {start: None}
    came_from_goal = {goal: None}
    cost_so_far_start = {start: 0}
    cost_so_far_goal = {goal: 0}
    explored_nodes = []
    node_id_map = {}  # 노드 ID 매핑을 위한 딕셔너리
    node_counter = 0
    current_best_path = None  # 현재까지의 최단 경로
    best_cost = float('inf')

    def reconstruct_path(current, came_from_dict):
        path = []
        while current is not None:
            path.append(current)
            current = came_from_dict[current]
        return path

    def add_explored_node(node, cost, previous_node, direction, temp_path=None):
        nonlocal node_counter
        node_id = str(node_counter)
        node_id_map[node] = node_id
        
        previous_node_id = None
        if previous_node is not None and previous_node in node_id_map:
            previous_node_id = node_id_map[previous_node]

        # 현재 노드까지의 임시 최단 경로가 있다면 포함
        current_path = None
        if temp_path:
            current_path = [
                {"lat": node_positions[n][0], "lng": node_positions[n][1]}
                for n in temp_path
            ]

        explored_nodes.append({
            "id": node_id,
            "lat": node_positions[node][0],
            "lng": node_positions[node][1],
            "cost": cost,
            "previousNode": previous_node_id,
            "direction": direction,
            "tempPath": current_path  # 임시 최단 경로 추가
        })
        node_counter += 1
        return node_id

    while frontier_start and frontier_goal:
        # 출발지에서 탐색
        _, current_start = heapq.heappop(frontier_start)
        
        # 현재까지의 경로 복원
        temp_path_start = reconstruct_path(current_start, came_from_start)[::-1]
        
        current_start_id = add_explored_node(
            current_start,
            cost_so_far_start[current_start],
            came_from_start[current_start],
            "forward",
            temp_path_start
        )

        if current_start in cost_so_far_goal:
            total_cost = cost_so_far_start[current_start] + cost_so_far_goal[current_start]
            if total_cost < best_cost:
                best_cost = total_cost
                meeting_node = current_start
                current_best_path = temp_path_start
            break

        for neighbor, cost in adjacency_list.get(current_start, []):
            new_cost = cost_so_far_start[current_start] + cost
            if neighbor not in cost_so_far_start or new_cost < cost_so_far_start[neighbor]:
                cost_so_far_start[neighbor] = new_cost
                priority = new_cost + haversine(
                    node_positions[neighbor][0], node_positions[neighbor][1],
                    node_positions[goal][0], node_positions[goal][1]
                )
                heapq.heappush(frontier_start, (priority, neighbor))
                came_from_start[neighbor] = current_start

        # 도착지에서 탐색
        _, current_goal = heapq.heappop(frontier_goal)
        
        # 현재까지의 경로 복원
        temp_path_goal = reconstruct_path(current_goal, came_from_goal)
        
        current_goal_id = add_explored_node(
            current_goal,
            cost_so_far_goal[current_goal],
            came_from_goal[current_goal],
            "backward",
            temp_path_goal
        )

        if current_goal in cost_so_far_start:
            total_cost = cost_so_far_start[current_goal] + cost_so_far_goal[current_goal]
            if total_cost < best_cost:
                best_cost = total_cost
                meeting_node = current_goal
                current_best_path = temp_path_goal
            break

        for neighbor, cost in adjacency_list.get(current_goal, []):
            new_cost = cost_so_far_goal[current_goal] + cost
            if neighbor not in cost_so_far_goal or new_cost < cost_so_far_goal[neighbor]:
                cost_so_far_goal[neighbor] = new_cost
                priority = new_cost + haversine(
                    node_positions[neighbor][0], node_positions[neighbor][1],
                    node_positions[start][0], node_positions[start][1]
                )
                heapq.heappush(frontier_goal, (priority, neighbor))
                came_from_goal[neighbor] = current_goal

    # 최종 경로 재구성
    path_from_start = []
    current = meeting_node
    while current is not None:
        path_from_start.append(current)
        current = came_from_start[current]
    path_from_start.reverse()

    path_from_goal = []
    current = meeting_node
    while current is not None:
        if current != meeting_node:
            path_from_goal.append(current)
        current = came_from_goal[current]

    final_path = path_from_start + path_from_goal

    return final_path, explored_nodes