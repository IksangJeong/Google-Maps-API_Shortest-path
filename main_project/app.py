from flask import Flask, request, jsonify, render_template
from pathfinder import Coordinate, PathFinder
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# Google Maps API 키
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

@app.route('/')
def home():
    """메인 페이지 렌더링"""
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

@app.route('/api/route', methods=['POST'])
def find_route():
    """좌표 기반 최단 경로 찾기"""
    try:
        data = request.get_json()
        print("Received data:", data)  # 입력 데이터 로깅
        
        start_coord = Coordinate(data['origin']['lat'], data['origin']['lng'])
        end_coord = Coordinate(data['destination']['lat'], data['destination']['lng'])
        
        print(f"Start coordinates: {start_coord}")  # 시작 좌표 로깅
        print(f"End coordinates: {end_coord}")      # 끝 좌표 로깅
        
        # 새로운 PathFinder 인스턴스 생성
        path_finder = PathFinder()
        
        # 도로망 생성
        print("Creating road network...")  # 도로망 생성 시작 로깅
        start_id, end_id = path_finder.create_road_network(start_coord, end_coord)
        print(f"Network created. Start ID: {start_id}, End ID: {end_id}")  # 도로망 생성 결과 로깅
        print(f"Number of nodes in network: {len(path_finder.nodes)}")     # 노드 수 로깅
        
        # 최단 경로 찾기
        print("Finding shortest path...")  # 경로 탐색 시작 로깅
        path, total_distance = path_finder.find_shortest_path(start_id, end_id)
        print(f"Path found: {bool(path)}, Distance: {total_distance}")  # 경로 탐색 결과 로깅
        
        if not path:
            return jsonify({
                'success': False,
                'error': '경로를 찾을 수 없습니다.'
            }), 404
            
        # 경로 상세 정보 계산
        path_details = path_finder.get_path_details(path)
        
        # 응답 데이터 구성
        response_data = {
            'success': True,
            'path': [{'lat': coord.lat, 'lng': coord.lng} for coord in path],
            'total_distance': f"{path_details['total_distance']:.2f}km",
            'segments': [
                {
                    'start': {'lat': seg['start'].lat, 'lng': seg['start'].lng},
                    'end': {'lat': seg['end'].lat, 'lng': seg['end'].lng},
                    'distance': f"{seg['distance']:.2f}km",
                    'direction': seg['direction']
                }
                for seg in path_details['segments']
            ]
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)