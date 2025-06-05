# app/app.py

import os
import sys

from app.services.crawler.news.news_crawler import get_news_response

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
from app.services.intent_classifier import predict_intent

# 루트를 sys.path에 추가했으므로 아래 import가 정상 작동함

from app.services.crawler.news import news_crawler as chatbot
from data import database as db
from data import config

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")
CORS(app)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify({
        "API_URL": f"http://{config.HOST}:{config.PORT}/api",
        "THEME_COLOR": "#4a6fa5"
    })



@app.route("/api/movie", methods=["GET"])
def movie_api():
    movie_data = get_movie_chart()
    return jsonify(movie_data)

@app.route("/api/intent", methods=["POST"])
def intent_api():
    data = request.get_json()
    user_text = data.get("text", "")
    if not user_text:
        return jsonify({"status": "error", "message": "텍스트가 필요합니다."}), 400

    intent = predict_intent(user_text)
    return jsonify({"intent": intent})


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        user_id = data.get("user_id", "anonymous")

        # 1) 입력값 검증
        if not user_message:
            return jsonify({"status": "prompt", "message": "검색어를 입력해주세요."}), 400
        if not user_id:
            return jsonify({"status": "error", "message": "user_id가 필요합니다."}), 400

        # 2) 과거 대화 불러오기 (예: 요약 저장용)
        history = db.get_conversation_history(user_id, limit=5)

        # 3) 사용자의 의도 분류 (intent: "movies", "news", 등)
        user_intent = predict_intent(user_message)

        # 4) 의도에 따라 분기 처리
        if user_intent == "movie":
            movie_data = get_movie_chart()
            response_data = {
                "status": "success",
                "intent": "movies",
                "data": movie_data,
                "message": movie_data,
                "summary": movie_data
            }


        elif user_intent == "news":

            news_result = get_news_response(user_message, history)
            summary = news_result.get("summary", "")
            response_data = {
                "status": news_result.get("status", "error"),
                "intent": "news",
                "summary": summary,
                "raw": news_result,
                "message": summary
            }

        else:
            # 그 외 의도 처리 (QA, 일반 대화 등)
            response_data = {
                "status": "error",
                "intent": user_intent,
                "message": "처리할 수 없는 의도입니다."
            }

        # 5) DB에 대화 저장 (예: 성공했을 때만)
        if response_data.get("status") == "success":
            # 영화 차트는 summary 개념이 없으므로
            # 영화 차트 같은 경우 user_message 대신 제목으로 저장하거나,
            # news 요약은 response_data["summary"]로 저장
            if user_intent == "movie":
                # 영화 차트는 따로 요약 텍스트가 없으므로, title=user_message, response=""로 저장 예시
                title = user_message[:10] + ("..." if len(user_message) > 10 else "")
                db.save_conversation(user_id, title, "", "")
            else:
                title = user_message[:10] + ("..." if len(user_message) > 10 else "")
                summary_text = response_data.get("summary", "")
                db.save_conversation(user_id, title, user_message, summary_text)

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"status": "error", "message": f"서버 오류: {str(e)}"}), 500



@app.route("/api/reset", methods=["POST"])
def reset_conversation():
    data = request.get_json()
    user_id = data.get("user_id", "anonymous")
    db.clear_conversation_history(user_id)
    return jsonify({"status": "success", "message": "대화가 초기화되었습니다."})


if __name__ == "__main__":
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
