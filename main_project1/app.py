from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# 환경 변수 설정
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['DEBUG'] = True
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# 기본 라우트
@app.route('/')
def home():
    """메인 페이지 렌더링"""
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

# API 엔드포인트 - 경로 찾기
@app.route('/api/path', methods=['POST'])
def find_path():
    """경로 찾기 API"""
    try:
        data = request.get_json()
        start = data.get('start')
        end = data.get('end')
        
        if not start or not end:
            return jsonify({
                'error': '출발지와 도착지를 모두 지정해주세요.'
            }), 400

        # TODO: 경로 찾기 알고리즘 구현
        return jsonify({
            'message': '경로 찾기 기능 구현 예정',
            'start': start,
            'end': end
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 에러 핸들러
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': '페이지를 찾을 수 없습니다.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '서버 에러가 발생했습니다.'}), 500

if __name__ == '__main__':
    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("Google Maps API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    app.run(debug=True)