import osmnx as ox

def load_dynamic_graph(start, end):
    """
    주어진 출발지와 도착지 좌표를 기반으로 그래프를 로드.
    :param start: 출발지 좌표 {"lat": ..., "lng": ...}
    :param end: 도착지 좌표 {"lat": ..., "lng": ...}
    :return: 로드된 도로 그래프
    """
    north = max(start["lat"], end["lat"]) + 0.01
    south = min(start["lat"], end["lat"]) - 0.01
    east = max(start["lng"], end["lng"]) + 0.01
    west = min(start["lng"], end["lng"]) - 0.01

    print(f"Graph bounding box: north={north}, south={south}, east={east}, west={west}")

    # 범위 내 도로 그래프 로드
    graph = ox.graph_from_bbox(
        north=north,
        south=south,
        east=east,
        west=west,
        network_type="drive",
    )
    return graph
