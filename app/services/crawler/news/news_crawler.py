import re
import logging
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sklearn.feature_extraction.text import TfidfVectorizer
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.WARNING)

def get_news_response(user_message, _=None):
    query = user_message.strip()
    if not query:
        return {"status": "prompt", "message": "검색어를 입력해주세요."}

    result = crawl_news(query, max_links=10)
    if result['status'] == 'success':
        first_sentence = result['summary'].split('.')[0].strip()
        result['title'] = first_sentence[:30] or query
    return result


def crawl_news(query, max_links=10):
    links = get_naver_news_links(query, max_links)
    logging.info(f"[{query}] 수집된 뉴스 링크 수: {len(links)}")

    if not links:
        return {
            "status": "no_results",
            "query": query,
            "summary": "관련 뉴스 기사를 찾을 수 없습니다.",
            "results": []
        }

    results = []
    full_texts = []
    seen_links = set()

    with ThreadPoolExecutor(max_workers=5) as executor:
        contents = list(executor.map(fetch_naver_article_content, links))

    for link, content in zip(links, contents):
        if not content or link in seen_links or len(content.strip()) < 70:
            continue
        seen_links.add(link)
        title = extract_title_from_content(content)
        results.append({
            "title": title or link.split('/')[-1],
            "link": link,
            "snippet": content[:100] + "..." if len(content) > 100 else content
        })
        full_texts.append(content)

    if not full_texts:
        return {
            "status": "success",
            "query": query,
            "summary": "본문 요약이 어려웠습니다. 아래 뉴스 링크를 참고해보세요.",
            "results": results
        }

    cleaned_texts = clean_texts(full_texts)
    summary = summarize(cleaned_texts, query) if cleaned_texts else "요약할 내용이 충분하지 않습니다."

    return {
        "status": "success",
        "query": query,
        "summary": summary,
        "results": results
    }


def get_naver_news_links(query, max_links=10):
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://search.naver.com/search.naver?where=news&query={query}"
    try:
        res = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = []
        for a in soup.select('a[href*="naver.com"]'):
            href = a.get('href')
            if not href or any(sub in href for sub in ['promotion', 'event', 'static']):
                continue
            if re.search(r'(news|sports|entertain)\.naver\.com', href) and href not in links:
                links.append(href)
            if len(links) >= max_links:
                break
        return links
    except Exception as e:
        logging.warning(f"뉴스 링크 수집 실패: {e}")
        return []


def fetch_naver_article_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        selectors = [
            '#dic_area', '#articleBodyContents', '#newsct_article',
            '#articeBody', 'article', '.newsct_article', '.content'
        ]
        for selector in selectors:
            tag = soup.select_one(selector)
            if tag and len(tag.get_text(strip=True)) > 70:
                return tag.get_text(strip=True)

        og_desc = soup.select_one('meta[property="og:description"]')
        if og_desc and og_desc.get("content") and len(og_desc["content"].strip()) > 50:
            return og_desc["content"].strip()

        if soup.title:
            return soup.title.get_text(strip=True)

        return ""
    except Exception as e:
        logging.warning(f"뉴스 본문 수집 실패 - URL: {url} / 에러: {e}")
        return ""


def extract_title_from_content(content):
    sentences = re.split(r'[.!?]', content)
    return sentences[0].strip() if sentences else ""


def clean_texts(texts):
    seen = set()
    return [
        re.sub(r'\s+', ' ', t.strip())
        for t in texts
        if len(t.strip()) >= 30 and not (t in seen or seen.add(t))
    ]


def summarize(texts, query, max_sentences=3):
    joined = ' '.join(texts)
    sentences = [s.strip() for s in re.split(r'[.!?]', joined) if len(s.strip()) > 50]

    if not sentences:
        return "요약할 수 있는 정보가 부족합니다."

    keyword_sentences = [s for s in sentences if query in s]
    keyword_sentences = keyword_sentences[:1]
    remaining_sentences = [s for s in sentences if s not in keyword_sentences]

    if not remaining_sentences:
        return ' '.join(keyword_sentences)

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([query] + remaining_sentences)
    scores = (matrix[1:] @ matrix[0].T).toarray().flatten()
    top_indices = np.argsort(scores)[::-1]

    selected = keyword_sentences + [
        remaining_sentences[i]
        for i in top_indices if remaining_sentences[i] not in keyword_sentences
    ]
    summary = ' '.join(selected[:max_sentences])
    return summary if summary.endswith('.') else summary + '.'