import os
import sys
import json
import torch
import joblib
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def resource_path(relative_path):
    """
    PyInstaller EXE, 개발환경 모두에서 안전하게 동작하는 경로 생성 함수
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# config.json 경로 안전하게 지정
config_path = resource_path(os.path.join("data", "config.json"))

# config 로드
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# 경로 설정 (모두 resource_path 적용)
exit_keywords = config["exit_keywords"]
model_path = resource_path(config["model_path"])
label_path = resource_path(config["label_path"])
save_path = resource_path(config["save_path"])
tokenizer_name = config["tokenizer_name"]

# 모델 및 토크나이저 로드
model = AutoModelForSequenceClassification.from_pretrained(model_path, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, trust_remote_code=True)

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
        if userText.lower() in exit_keywords:
            break
        userIntent = predict_intent(userText)
        print(f"예측된 의도: {userIntent}")
        intent_data.append({"text": userText, "intent": userIntent})

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(intent_data, f, ensure_ascii=False, indent=2)

# userIntent : 의도 변수
# userText : 입력된 한글 문장을 담는 변수

print("config_path =", config_path)
