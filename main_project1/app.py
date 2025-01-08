from flask import Flask, render_template, request, jsonify
from algorithms.shortest_path import RoadNetwork
from dotenv import load_dotenv
import os
import traceback

# .env 파일 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__, static_url_path='/static')

# 환경 변수 설정
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['DEBUG'] = True
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# 전역 RoadNetwork 인스턴스
road_network = RoadNetwork()

@app.route('/')
def home():
    """메인 페이지 렌더링"""
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

@app.route('/api/path', methods=['POST'])
def find_shortest_path():
    """경로 찾기 API"""
    print("Route handler called")
    try:
        data = request.get_json()
        print("Received data:", data)
        
        start = data.get('start')
        end = data.get('end')
        
        if not start or not end:
            return jsonify({
                'error': '출발지와 도착지를 모두 지정해주세요.'
            }), 400

        print(f"Finding path from {start} to {end}")
        # 도로 네트워크 로드
        center_lat = (start['lat'] + end['lat']) / 2
        center_lng = (start['lng'] + end['lng']) / 2
        
        print("Loading road network...")
        road_network.load_network(center_lat, center_lng)
        
        # 경로 찾기
        print("Finding path...")
        visualization_steps = road_network.find_path(
            start['lat'], start['lng'],
            end['lat'], end['lng']
        )
        
        print(f"Found path with {len(visualization_steps)} steps")
        
        if not visualization_steps:
            return jsonify({
                'error': '경로를 찾을 수 없습니다.'
            }), 404
            
        return jsonify({
            'success': True,
            'steps': visualization_steps
        })

    except Exception as e:
        print("Error occurred:", str(e))
        print(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': '요청한 페이지를 찾을 수 없습니다.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    # Flask 애플리케이션 실행
    print("Starting Flask application...")
    print(f"API Key: {GOOGLE_MAPS_API_KEY[:5]}...")  # API 키의 처음 5자리만 표시
    print("Available routes:")
    print("  - /")
    print("  - /api/path [POST]")
    app.run(debug=True, host='127.0.0.1', port=5000)