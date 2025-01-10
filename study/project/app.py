from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """메인 페이지 렌더링"""
    return render_template('index.html')

@app.route('/locations', methods=['GET'])
def locations():
    """장소 좌표 데이터 반환"""
    data = [
        {"name": "경복궁", "lat": 37.579617, "lng": 126.977041},
        {"name": "무령왕릉", "lat": 36.444117, "lng": 127.119045},
        {"name": "불국사", "lat": 35.789361, "lng": 129.331127}
    ]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)