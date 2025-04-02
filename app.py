from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import config
import chat_engine as chatbot
import database as db
import json  # JSON 문자열 파싱을 위해 추가

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/config', methods=['GET'])
def get_config():
    return jsonify({
        "API_URL": f"http://{config.HOST}:{config.PORT}/api",
        "THEME_COLOR": "#4a6fa5"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    user_id = data.get('user_id', 'anonymous')

    history = db.get_conversation_history(user_id, limit=5)

    # get_response()는 JSON 문자열을 반환하므로 파싱 필요
    response_json = chatbot.get_response(user_message, history)
    response_data = json.loads(response_json)

    # 응답이 성공일 때만 대화 저장
    if response_data.get("status") == "success":
        db.save_conversation(user_id, user_message, response_data.get("summary", ""))

    return jsonify(response_data)  # 전체 JSON 그대로 반환

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    data = request.get_json()
    user_id = data.get('user_id', 'anonymous')
    db.clear_conversation_history(user_id)
    return jsonify({'status': 'success', 'message': '대화가 초기화되었습니다.'})

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
