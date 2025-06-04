# app/app.py

import os
import sys

# 1) 현재 파일(app.py) 위치 절대경로
current_file_path = os.path.abspath(__file__)  # .../2025ChatBot/app/app.py
project_root = os.path.dirname(os.path.dirname(current_file_path))  # .../2025ChatBot
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ──────────────────────────────

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json

from app.services.crawler.movie.movie_crawler import get_movie_chart
from app.services import intent_classifier

# 루트를 sys.path에 추가했으므로 아래 import가 정상 작동함

from app.services.crawler.news import chat_engine as chatbot
from data import database as db
from data import config

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")
CORS(app)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/config", methods=["GET"])
def get_config():
    return jsonify({
        "API_URL": f"http://{config.HOST}:{config.PORT}/api",
        "THEME_COLOR": "#4a6fa5"
    })



@app.route("/api/movies", methods=["GET"])
def movie_api():
    movie_data = get_movie_chart()
    return jsonify(movie_data)

@app.route("/api/intent", methods=["POST"])
def intent_api():
    data = request.get_json()
    user_text = data.get("text", "")
    if not user_text:
        return jsonify({"status": "error", "message": "텍스트가 필요합니다."}), 400

    intent = intent_classifier(user_text)
    return jsonify({"intent": intent})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    user_id = data.get("user_id", "anonymous")

    history = db.get_conversation_history(user_id, limit=5)

    response_json = chatbot.get_response(user_message, history)
    response_data = json.loads(response_json)


    if response_data.get("status") == "success":
        db.save_conversation(user_id, user_message, response_data.get("summary", ""))

    return jsonify(response_data)


@app.route("/api/reset", methods=["POST"])
def reset_conversation():
    data = request.get_json()
    user_id = data.get("user_id", "anonymous")
    db.clear_conversation_history(user_id)
    return jsonify({"status": "success", "message": "대화가 초기화되었습니다."})


if __name__ == "__main__":
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
