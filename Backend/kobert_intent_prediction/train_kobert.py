from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

# 데이터 준비
df = pd.read_csv("train.csv")
label_encoder = LabelEncoder()
df["labels"] = label_encoder.fit_transform(df["label"])
joblib.dump(label_encoder, "label_encoder.pkl")

dataset = Dataset.from_pandas(df[["text", "labels"]])

# 토크나이저 및 모델 로드
model_name = "monologg/kobert"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(label_encoder.classes_), trust_remote_code=True)

# 토크나이징 함수
def tokenize(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=64)

tokenized_dataset = dataset.map(tokenize)

# 훈련 설정
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=16,
    num_train_epochs=3,
    evaluation_strategy="no",
    logging_dir="./logs"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset
)

trainer.train()

# 모델만 저장 (tokenizer는 저장 생략)
model.save_pretrained("./kobert_intent_model")