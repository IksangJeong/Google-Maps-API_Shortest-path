from flask import Flask, jsonify, request, render_template
from algorithms.path_finder import (
    a_star_search,
    bidirectional_a_star,
    prepare_graph,
    get_closest_node,
)
from algorithms.road_network import load_dynamic_graph
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# Google Maps API 키 로드
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

@app.route("/")
def index():
    return render_template("index.html", api_key=GOOGLE_MAPS_API_KEY)

@app.route("/find-path", methods=["POST"])
def find_path():
    try:
        data = request.json
        start = data.get("start")
        end = data.get("end")

        if not start or not end:
            return jsonify({"error": "Start or End coordinates are missing"}), 400

        # 선택된 좌표를 기준으로 그래프 로드
        graph = load_dynamic_graph(start, end)

        # 그래프 준비
        node_positions, adjacency_list = prepare_graph(graph)

        # 가장 가까운 노드 찾기
        start_node = get_closest_node(start["lat"], start["lng"], node_positions)
        end_node = get_closest_node(end["lat"], end["lng"], node_positions)

        # 양방향 A* 경로 탐색
        path, explored_nodes = bidirectional_a_star(
            start_node, end_node, node_positions, adjacency_list
        )

        # 경로와 탐색 과정 좌표로 변환
        path_coords = [
            {"lat": node_positions[node][0], "lng": node_positions[node][1]}
            for node in path
        ]
        explored_coords = [
            {
                "lat": node_positions[node][0],
                "lng": node_positions[node][1],
                "cost": explored_nodes[node],
            }
            for node in explored_nodes
        ]

        return jsonify({"path": path_coords, "exploredNodes": explored_coords})
    except Exception as e:
        print("Error in /find-path:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
