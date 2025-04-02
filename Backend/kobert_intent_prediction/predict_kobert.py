from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
import joblib

# 모델 로드
model = AutoModelForSequenceClassification.from_pretrained("./kobert_intent_model", trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("monologg/kobert", trust_remote_code=True)

# 라벨 로드
label_encoder = joblib.load("label_encoder.pkl")
labels = list(label_encoder.classes_)

def predict_intent(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=64)
    outputs = model(**inputs)
    logits = outputs.logits
    predicted = torch.argmax(logits, dim=1).item()
    return labels[predicted]

# 테스트 실행
if __name__ == "__main__":
    while True:
        text = input("입력 문장: ")
        if text.lower() in ["exit", "quit", "종료"]:
            break
        intent = predict_intent(text)
        print(f"예측된 의도: {intent}")