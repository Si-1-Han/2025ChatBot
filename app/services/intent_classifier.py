import os
import json
import torch
import joblib
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 기준 디렉토리 = 현재 파일의 경로
BASE_DIR = os.path.dirname(__file__)

# 경로 설정
model_path = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'model', 'kobert_intent_model'))
label_path = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'model', 'label_encoder.pkl'))
save_path = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'data', 'intent_data.json'))

# 모델 및 토크나이저 로드
model = AutoModelForSequenceClassification.from_pretrained(model_path, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("monologg/kobert", trust_remote_code=True)

# 라벨 인코더 로드
label_encoder = joblib.load(label_path)
labels = list(label_encoder.classes_)

# 예측 함수
def predict_intent(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=64)
    outputs = model(**inputs)
    logits = outputs.logits
    predicted = torch.argmax(logits, dim=1).item()
    return labels[predicted]

# 예제 실행 (터미널에서 테스트할 때만 실행)
if __name__ == "__main__":
    intent_data = []

    while True:
        userText = input("무엇이 궁금하신가요? : ")
        if userText.lower() in ["exit", "quit", "종료"]:
            break
        userIntent = predict_intent(userText)
        print(f"예측된 의도: {userIntent}")
        intent_data.append({"text": userText, "intent": userIntent})

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(intent_data, f, ensure_ascii=False, indent=2)

# userIntent : 의도 변수
# userText : 입력된 한글 문장을 담는 변수
# pip install -r requirements.txt 로 필수 패키지 설치가능