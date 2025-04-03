import requests
from bs4 import BeautifulSoup
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_response(user_message):
    return crawl_naver_news_improved(user_message)


def crawl_naver_news_improved(query):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    url = f"https://search.naver.com/search.naver?where=news&query={query}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    news_items = soup.select(".news_area")

    if not news_items:
        return {"status": "no_results", "message": f"'{query}'에 대한 결과를 찾지 못했어요."}

    results = []
    full_texts = []

    for item in news_items[:5]:
        title_tag = item.select_one("a.news_tit")
        desc_tag = item.select_one(".dsc_wrap")

        if not title_tag:
            continue

        title = title_tag['title']
        link = title_tag['href']
        snippet = desc_tag.get_text(strip=True) if desc_tag else ""

        content = ""
        if "news.naver.com" in link:
            try:
                article_res = requests.get(link, headers=headers, timeout=5)
                article_soup = BeautifulSoup(article_res.text, 'html.parser')

                # ✅ 여러 백업 선택자 시도
                candidate_selectors = [
                    "div#newsct_article p",        # 최신
                    "div#articleBodyContents p",   # 구버전
                    "div#articeBody p",            # 일부 케이스
                    "div.article_body p",          # 언론사별 특화
                ]

                for selector in candidate_selectors:
                    paragraphs = article_soup.select(selector)
                    if paragraphs:
                        content = " ".join([
                            p.get_text(strip=True)
                            for p in paragraphs if len(p.get_text(strip=True)) > 30
                        ])
                        if content:
                            break  # 본문 확보되면 종료

                # 광고 필터링
                if any(stop_word in content for stop_word in ["무단전재", "재배포", "기사원문"]):
                    content = ""

            except Exception as e:
                print("❌ 본문 크롤링 실패:", e)

        # 콘텐츠 없을 경우 스니펫 사용
        if content:
            full_texts.append(content)
        elif snippet:
            full_texts.append(snippet)

        results.append({
            "title": title,
            "link": link,
            "snippet": snippet
        })

    summary = summarize_texts(full_texts)

    return {
        "status": "success",
        "query": query,
        "summary": summary,
        "results": results
    }


def summarize_texts(texts, max_sentences=3, similarity_threshold=0.8):
    sentences = []
    for text in texts:
        parts = re.split(r"[.!?]", text)
        parts = [s.strip() for s in parts if len(s.strip()) > 30]
        sentences.extend(parts)

    if not sentences:
        return "요약할 수 있는 정보가 부족합니다."

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)
    scores = X.sum(axis=1).A1
    ranked_indices = np.argsort(scores)[::-1]

    selected = []
    for idx in ranked_indices:
        if len(selected) >= max_sentences:
            break
        if all(cosine_similarity(X[idx], X[i])[0][0] < similarity_threshold for i in selected):
            selected.append(idx)

    summary = " ".join([sentences[i] for i in selected])
    return summary + "."
