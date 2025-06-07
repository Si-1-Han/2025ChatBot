# app/app.py

import os
import sys

from app.services.crawler.news.news_crawler import get_news_response
from app.services.crawler.goods.goods_crawler import get_goods
from app.services.crawler.stock.stock_crawler import get_stock

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

        history = db.get_conversation_history(user_id, limit=5)

        user_intent = predict_intent(user_message)

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

        elif user_intent == "goods":
            goods_data = get_goods(user_message)
            response_data = {
                "status": "success",
                "intent": "goods",
                "data": goods_data,
                "message": goods_data
            }
        elif user_intent == "stock":
            stock_data = get_stock()
            response_data = {
                "status": "success",
                "intent": "stock",
                "data": stock_data,
                "message": stock_data
            }
        else:
            response_data = {
                "status": "error",
                "intent": user_intent,
                "message": "처리할 수 없는 의도입니다."
            }

        if response_data.get("status") == "success":
            if user_intent == "movie":
                title = user_message[:10] + ("..." if len(user_message) > 10 else "")
                db.save_conversation(user_id, title, "", "")
            else:
                title = user_message[:10] + ("..." if len(user_message) > 10 else "")
                summary_text = json.dumps(response_data.get("message", ""), ensure_ascii=False)
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
