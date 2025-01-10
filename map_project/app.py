from flask import Flask, jsonify, request, render_template, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from algorithms.path_finder import (
    a_star_search,
    bidirectional_a_star,
    prepare_graph,
    get_closest_node,
)
from algorithms.road_network import load_dynamic_graph
from dotenv import load_dotenv
import os
import secrets
import math

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Google Maps API 키 로드
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# 채팅방 정보를 저장할 딕셔너리
rooms = {}

def haversine(lat1, lon1, lat2, lon2):
    """두 지점 간의 대원 거리 계산 (단위: m)"""
    R = 6371000  # 지구 반경 (미터)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.route("/")
def index():
    return render_template("index.html", api_key=GOOGLE_MAPS_API_KEY)

@app.route("/create-room", methods=["POST"])
def create_room():
    room_id = secrets.token_urlsafe(8)  # 랜덤한 방 ID 생성
    rooms[room_id] = {
        "users": [],
        "locations": {}
    }
    return jsonify({"room_id": room_id})

@app.route("/join/<room_id>")
def join_chat_room(room_id):
    if room_id not in rooms:
        return "잘못된 방 코드입니다.", 404
    return render_template("index.html", api_key=GOOGLE_MAPS_API_KEY, room_id=room_id)

@socketio.on('join')
def on_join(data):
    try:
        username = data['username']
        room = data['room']
        if room in rooms:
            join_room(room)
            if username not in rooms[room]["users"]:
                rooms[room]["users"].append(username)
            
            # 방에 있는 모든 사람에게 새로운 참가자 알림
            emit('user_joined', {
                'username': username,
                'users': rooms[room]["users"]
            }, room=room)
            
            # 새로 들어온 사람에게 현재 방의 상태 전송
            emit('room_status', {
                'users': rooms[room]["users"],
                'locations': rooms[room]["locations"]
            }, room=request.sid)
            
            print(f"User {username} joined room {room}. Current users: {rooms[room]['users']}")
    except Exception as e:
        print(f"Error in on_join: {str(e)}")

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    if room in rooms:
        leave_room(room)
        if username in rooms[room]["users"]:
            rooms[room]["users"].remove(username)
            if username in rooms[room]["locations"]:
                del rooms[room]["locations"][username]
        emit('user_left', {
            'username': username,
            'users': rooms[room]["users"]
        }, room=room)

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')

@socketio.on('send_message')
def handle_message(data):
    room = data.get('room')
    if room and room in rooms:
        # 위치 정보가 포함된 메시지인 경우 저장
        if data.get('type') == 'location':
            rooms[room]["locations"][data['username']] = {
                "location": data['location'],
                "address": data['address']
            }
        emit('receive_message', data, room=room)

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
        node_positions, adjacency_list = prepare_graph(graph)

        # 가장 가까운 노드 찾기
        start_node = get_closest_node(start["lat"], start["lng"], node_positions)
        end_node = get_closest_node(end["lat"], end["lng"], node_positions)

        # 양방향 A* 경로 탐색
        path, explored_nodes = bidirectional_a_star(
            start_node, end_node, node_positions, adjacency_list
        )

        # 경로를 좌표로 변환
        path_coords = [
            {"lat": node_positions[node][0], "lng": node_positions[node][1]}
            for node in path
        ]

        return jsonify({
            "path": path_coords,
            "exploredNodes": explored_nodes
        })

    except Exception as e:
        print("Error in /find-path:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/find-midpoint", methods=["POST"])
def find_midpoint():
    try:
        data = request.json
        start = data.get("start")
        end = data.get("end")

        if not start or not end:
            return jsonify({"error": "두 위치 정보가 필요합니다"}), 400

        # 그래프 로드
        graph = load_dynamic_graph(start, end)
        node_positions, adjacency_list = prepare_graph(graph)

        # 가장 가까운 노드 찾기
        start_node = get_closest_node(start["lat"], start["lng"], node_positions)
        end_node = get_closest_node(end["lat"], end["lng"], node_positions)

        # 최단 경로 찾기
        path, _ = bidirectional_a_star(start_node, end_node, node_positions, adjacency_list)

        # 경로를 좌표로 변환
        path_coords = [
            {"lat": node_positions[node][0], "lng": node_positions[node][1]}
            for node in path
        ]

        # 경로의 중간지점 찾기 (전체 경로 길이의 50% 지점)
        total_distance = 0
        distances = []
        
        for i in range(len(path_coords) - 1):
            point1 = path_coords[i]
            point2 = path_coords[i + 1]
            segment_distance = haversine(
                point1["lat"], point1["lng"],
                point2["lat"], point2["lng"]
            )
            total_distance += segment_distance
            distances.append(segment_distance)

        half_distance = total_distance / 2
        current_distance = 0

        # 중간지점이 있는 세그먼트 찾기
        for i, distance in enumerate(distances):
            current_distance += distance
            if current_distance >= half_distance:
                # 해당 세그먼트에서의 정확한 위치 계산
                remaining = current_distance - half_distance
                ratio = remaining / distance
                midpoint = {
                    "lat": path_coords[i]["lat"] + (path_coords[i+1]["lat"] - path_coords[i]["lat"]) * (1-ratio),
                    "lng": path_coords[i]["lng"] + (path_coords[i+1]["lng"] - path_coords[i]["lng"]) * (1-ratio)
                }
                return jsonify({
                    "path": path_coords,
                    "midpoint": midpoint,
                    "total_distance": total_distance
                })

        # 경로가 너무 짧은 경우
        return jsonify({
            "path": path_coords,
            "midpoint": path_coords[len(path_coords)//2],
            "total_distance": total_distance
        })

    except Exception as e:
        print("Error in /find-midpoint:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0',port = 5001)