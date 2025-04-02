import requests
from bs4 import BeautifulSoup
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def crawl_naver_news(query):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    url = f"https://search.naver.com/search.naver?where=news&query={query}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {
            "status": "error",
            "message": "네이버 뉴스 검색에 실패했습니다.",
            "results": []
        }

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(".news_area")

    if not items:
        return {
            "status": "no_results",
            "message": f"'{query}'에 대한 뉴스 결과를 찾지 못했어요.",
            "results": []
        }

    results = []
    full_texts = []

    for item in items[:3]:
        title_tag = item.select_one("a.news_tit")
        desc_tag = item.select_one("div.dsc_wrap")

        if not title_tag:
            continue

        title = title_tag['title']
        link = title_tag['href']
        snippet = desc_tag.get_text(strip=True) if desc_tag else ""

        # 본문 크롤링 (요약용)
        content = ""
        try:
            article_res = requests.get(link, headers=headers, timeout=5)
            article_soup = BeautifulSoup(article_res.text, 'html.parser')
            paragraphs = article_soup.find_all("p")
            content = ' '.join(
                p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30
            )
        except Exception as e:
            print(f"❌ 본문 크롤링 실패: {e}")

        if content:
            full_texts.append(content)

        results.append({
            "title": title,
            "link": link,
            "snippet": snippet
        })

    cleaned = clean_texts(full_texts)
    summary = summarize(cleaned, query)

    return {
        "status": "success",
        "query": query,
        "summary": summary,
        "results": results
    }

def clean_texts(text_list):
    seen = set()
    cleaned = []
    for text in text_list:
        text = re.sub(r'\s+', ' ', text.strip())
        if len(text) < 30 or text in seen or "네이버" in text:
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned

def summarize(texts, query, max_sentences=3):
    sentences = re.split(r'[.!?]', ' '.join(texts))
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    if not sentences:
        return "요약할 수 있는 정보가 부족합니다."

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([query] + sentences)
    query_vec = vectors[0]
    sentence_vecs = vectors[1:]

    scores = (sentence_vecs @ query_vec.T).toarray().flatten()

    top_indices = np.argsort(scores)[::-1][:max_sentences]
    top_sentences = [sentences[i] for i in top_indices]

    return ' '.join(top_sentences) + '.'

def get_response(user_message, conversation_history=[]):
    if not user_message.strip():
        return json.dumps({
            "status": "prompt",
            "message": "안녕하세요! 어떤 정보를 찾아드릴까요? 😊"
        }, ensure_ascii=False)

    return json.dumps(crawl_naver_news(user_message), ensure_ascii=False, indent=2)
