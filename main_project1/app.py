from flask import Flask, render_template, request, jsonify
from algorithms.shortest_path import PathFinder
from dotenv import load_dotenv
import os
import traceback

# .env 파일 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# 환경 변수 설정
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['DEBUG'] = True
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

@app.route('/')
def home():
    """메인 페이지 렌더링"""
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

@app.route('/api/path', methods=['POST'])
def find_path():
    """경로 찾기 API"""
    try:
        # 요청 데이터 확인
        data = request.get_json()
        print("Received data:", data)
        
        if not data:
            return jsonify({'error': '데이터가 없습니다.'}), 400

        start = data.get('start')
        end = data.get('end')
        
        print(f"Start coordinates: {start}")
        print(f"End coordinates: {end}")
        
        if not start or not end:
            return jsonify({
                'error': '출발지와 도착지를 모두 지정해주세요.'
            }), 400

        # 좌표 형식 확인
        required_keys = ['lat', 'lng']
        if not all(key in start for key in required_keys) or \
           not all(key in end for key in required_keys):
            return jsonify({
                'error': '잘못된 좌표 형식입니다.'
            }), 400

        try:
            # PathFinder 인스턴스 생성
            print("Creating PathFinder instance...")
            path_finder = PathFinder()
            
            # 격자 생성
            print("Creating grid...")
            start_id, end_id = path_finder.create_grid(
                (float(start['lat']), float(start['lng'])),
                (float(end['lat']), float(end['lng']))
            )
            print(f"Grid created. Start ID: {start_id}, End ID: {end_id}")
            
            # 최단 경로 찾기
            print("Finding shortest path...")
            visualization_steps = path_finder.find_shortest_path(start_id, end_id)
            print(f"Path found with {len(visualization_steps)} steps")
            
            return jsonify({
                'success': True,
                'steps': visualization_steps
            })
            
        except AttributeError as e:
            print("AttributeError:", str(e))
            print(traceback.format_exc())
            return jsonify({
                'error': 'PathFinder 클래스 메서드 호출 중 오류가 발생했습니다.'
            }), 500
            
        except Exception as e:
            print("Error during pathfinding:", str(e))
            print(traceback.format_exc())
            return jsonify({
                'error': '경로 찾기 중 오류가 발생했습니다.'
            }), 500

    except Exception as e:
        print("Unexpected error:", str(e))
        print(traceback.format_exc())
        return jsonify({
            'error': '서버 오류가 발생했습니다.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)