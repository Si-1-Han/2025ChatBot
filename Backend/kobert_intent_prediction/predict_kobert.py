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
# 리터럴 형식이 아닌 json 파일로 변경
if __name__ == "__main__":
    while True:
        userText = input("무엇이 궁금하신가요? : ")
        if userText.lower() in ["exit", "quit", "종료"]:
            break
        userIntent = predict_intent(userText)
        print(f"예측된 의도: {userIntent}")
        
# userIntent : 의도 변수
# userText : 입력된 한글 문장을 담는 변수