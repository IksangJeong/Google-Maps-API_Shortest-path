from flask import Flask, request, jsonify, render_template
from algorithms.path_finder import find_shortest_path
from algorithms.road_network import get_road_data
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Google Maps API Key (환경 변수에서 로드)
import os
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# 홈 라우트 - HTML 렌더링
@app.route('/')
def index():
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

# 좌표 데이터 처리 및 경로 계산
@app.route('/find-path', methods=['POST'])
def find_path():
    data = request.json
    start = data.get("start")
    end = data.get("end")

    # 도로 데이터 가져오기
    road_data = get_road_data(start, end)
    if not road_data:
        return jsonify({"error": "도로 데이터를 가져오는 데 실패했습니다."}), 500

    # 경로 탐색
    shortest_path = find_shortest_path(road_data, start, end)
    return jsonify({"path": shortest_path, "distance": road_data["distance"], "duration": road_data["duration"]})


if __name__ == '__main__':
    app.run(debug=True)
