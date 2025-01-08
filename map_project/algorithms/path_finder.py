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
    explored_nodes = {}

    while frontier_start and frontier_goal:
        # 출발지에서 탐색
        _, current_start = heapq.heappop(frontier_start)
        explored_nodes[current_start] = cost_so_far_start[current_start]

        if current_start in cost_so_far_goal:
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
        explored_nodes[current_goal] = cost_so_far_goal[current_goal]

        if current_goal in cost_so_far_start:
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

    # 경로 재구성
    meeting_node = current_start if current_start in cost_so_far_goal else current_goal
    path_from_start = []
    current = meeting_node
    while current is not None:
        path_from_start.append(current)
        current = came_from_start[current]

    path_from_goal = []
    current = meeting_node
    while current is not None:
        path_from_goal.append(current)
        current = came_from_goal[current]

    return path_from_start[::-1] + path_from_goal, explored_nodes
