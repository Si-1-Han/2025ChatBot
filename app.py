from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    bot_reply = f'"{user_message}"에 대한 답변입니다.'
    return jsonify({'response': bot_reply})

if __name__ == '__main__':
    app.run(debug=True)
