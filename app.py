from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import config
import chat_engine
import database as db

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/config')
def get_config():
    return jsonify({
        "API_URL": f"http://{config.HOST}:{config.PORT}/api",
        "THEME_COLOR": "#4a6fa5"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_id = data['user_id']
    message = data['message']
    chat_id = data.get('chat_id')

    if not chat_id:
        chat_id = db.create_chat(user_id)

    response_data = chat_engine.get_response(message)

    if response_data.get("status") == "success":
        db.save_message(chat_id, message, response_data["summary"])
    else:
        response_data["summary"] = "요약할 수 없습니다."

    return jsonify({**response_data, "chat_id": chat_id})

@app.route('/api/chats')
def chats():
    user_id = request.args.get("user_id")
    chat_list = db.get_chat_list(user_id)
    return jsonify({"status": "success", "chats": chat_list})

@app.route('/api/history/<int:chat_id>')
def history(chat_id):
    messages = db.get_chat_history_by_chat_id(chat_id)
    return jsonify({"status": "success", "history": messages})

@app.route('/api/delete/<int:chat_id>', methods=['DELETE'])
def delete(chat_id):
    db.delete_chat(chat_id)
    return jsonify({"status": "success", "message": "삭제되었습니다."})

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
