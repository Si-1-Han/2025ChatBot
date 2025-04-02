import requests
from bs4 import BeautifulSoup
import re

def crawl_google(query):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        # 👉 뉴스 탭에서 검색
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=nws"
        response = requests.get(url, headers=headers)

        print("✅ 상태코드:", response.status_code)
        if response.status_code != 200:
            return "웹 검색 중 문제가 발생했습니다."

        soup = BeautifulSoup(response.text, 'html.parser')

        # 👉 뉴스 제목 추출
        snippets = soup.select('div.BNeawe.vvjwJb.AP7Wnd')

        print("✅ 뉴스 결과 개수:", len(snippets))
        for s in snippets[:3]:
            print("📰", s.get_text())

        if not snippets:
            return f"'{query}'에 대한 뉴스를 찾지 못했어요."

        titles = [s.get_text() for s in snippets]
        return ' / '.join(titles[:3])
    except Exception as e:
        print("❌ 예외 발생:", e)
        return f"크롤링 오류: {e}"


def clean_texts(text_list):
    seen = set()
    cleaned = []

    for text in text_list:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)

        if len(text) < 30 or text in seen:
            continue

        if '더보기' in text or 'Google' in text:
            continue

        seen.add(text)
        cleaned.append(text)

    return cleaned

def summarize(texts, max_sentences=3):
    sentences = []

    for t in texts:
        parts = re.split(r'[.!?]', t)
        parts = [p.strip() for p in parts if len(p.strip()) > 20]
        sentences.extend(parts)

    if not sentences:
        return "요약할 수 있는 정보가 부족합니다."

    return ' '.join(sentences[:max_sentences]) + '.'

def get_response(user_message, conversation_history=[]):
    return crawl_google(user_message)