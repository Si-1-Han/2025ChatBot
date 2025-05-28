# movie_crawler.py

import requests
from bs4 import BeautifulSoup
import datetime
import json
import re
import os

def normalize_title(title):
    """한글/영문/숫자만 남기고 소문자로 정규화"""
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", title).lower()

def get_movie_chart_with_ticketing():
    # 1. KOBIS 박스오피스 데이터 가져오기
    kobis_api_key = "662d65ebb4eb2d7503390ff6d39f26fd"
    target_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    kobis_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": kobis_api_key, "targetDt": target_date}

    try:
        res = requests.get(kobis_url, params=params)
        res.raise_for_status()
        kobis_data = res.json()
    except Exception as e:
        print("❌ KOBIS API 에러:", e)
        return []

    movie_list = []
    for movie in kobis_data['boxOfficeResult']['dailyBoxOfficeList']:
        movie_list.append({
            "rank": movie['rank'],
            "title": movie['movieNm'],
            "open_date": movie['openDt'],
            "audience": movie['audiAcc'],
            "ticketing": "N/A"
        })

    # 2. CGV 예매율 데이터 크롤링
    selector_path = os.path.join(os.path.dirname(__file__), "selectors.json")
    try:
        with open(selector_path, "r", encoding="utf-8") as f:
            selectors = json.load(f)
        cgv_selectors = selectors["CGV"]
    except Exception as e:
        print("❌ selectors.json 읽기 오류:", e)
        return movie_list

    cgv_url = "http://www.cgv.co.kr/movies/?lt=1&ft=0"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        req = requests.get(cgv_url, headers=headers)
        soup = BeautifulSoup(req.text, "html.parser")
        movies = soup.select(cgv_selectors["movie_list"])

        cgv_data = {}
        for movie in movies:
            title_tag = movie.select_one(cgv_selectors["title"])
            ticketing_tag = movie.select_one(cgv_selectors["ticketing"])
            if title_tag and ticketing_tag:
                title = title_tag.text.strip()
                ticketing = ticketing_tag.text.strip()
                cgv_data[normalize_title(title)] = ticketing
    except Exception as e:
        print("❌ CGV 크롤링 오류:", e)
        return movie_list

    # 3. CGV 데이터와 매칭
    for movie in movie_list:
        norm_title = normalize_title(movie["title"])
        for cgv_title in cgv_data:
            if cgv_title in norm_title:
                movie["ticketing"] = cgv_data[cgv_title]
                break

    return movie_list

# 4. 직접 실행 시 출력
if __name__ == "__main__":
    movies = get_movie_chart_with_ticketing()
    if not movies:
        print("⚠️ 가져온 영화 데이터가 없습니다.")
    else:
        print("🎬 [박스오피스 순위 + CGV 예매율]")
        for movie in movies:
            print(f"{movie['rank']}위 - {movie['title']} | 개봉일: {movie['open_date']} | 누적관객: {movie['audience']}명 | 예매율: {movie['ticketing']}")

