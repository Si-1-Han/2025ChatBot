import requests
from bs4 import BeautifulSoup
import datetime
import json
import re
import os

def normalize_title(title):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", title).lower()

def get_movie_chart():
    kobis_api_key = "662d65ebb4eb2d7503390ff6d39f26fd"
    target_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    kobis_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": kobis_api_key, "targetDt": target_date}

    try:
        res = requests.get(kobis_url, params=params)
        res.raise_for_status()
        kobis_data = res.json()
    except Exception as e:
        # API 호출 실패 시 빈 리스트 형태로 반환
        print("KOBIS API 에러:", e)
        return format_movies([])

    # 박스오피스 리스트 수집
    movie_list = []
    for movie in kobis_data['boxOfficeResult']['dailyBoxOfficeList']:
        movie_list.append({
            "rank": movie['rank'],
            "title": movie['movieNm'],
            "open_date": movie['openDt'],
            "audience": movie['audiAcc'],
            "ticketing": "N/A"
        })

    # selectors.json 읽어서 CGV 크롤링용 셀렉터 가져오기
    selector_path = os.path.join(os.path.dirname(__file__), "selectors.json")
    try:
        with open(selector_path, "r", encoding="utf-8") as f:
            selectors = json.load(f)
        cgv_selectors = selectors["CGV"]
    except Exception as e:
        # selectors.json 읽기 실패 시에도 현재까지 모은 목록을 포맷하여 반환
        print("selectors.json 읽기 오류:", e)
        return format_movies(movie_list)

    # CGV 예매율 크롤링
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
        # CGV 크롤링 오류 시에도 movie_list 포맷 문자열을 반환
        print("CGV 크롤링 오류:", e)
        return format_movies(movie_list)

    # CGV 데이터와 매칭하여 ticketing 채우기
    for movie in movie_list:
        norm_title = normalize_title(movie["title"])
        for cgv_title, ticketing in cgv_data.items():
            if cgv_title in norm_title:
                movie["ticketing"] = ticketing
                break

    # 최종 결과를 문자열 형태로 반환
    return format_movies(movie_list)


def format_movies(movie_list):
    """
    movie_list를 콘솔에 출력하던 방식과 똑같은 포맷의 문자열로 만들어서 반환한다.
    """
    if not movie_list:
        return "⚠️ 가져온 영화 데이터가 없습니다.\n"

    lines = []
    lines.append("🎬 [박스오피스 순위와 CGV 예매율]")
    for movie in movie_list:
        rank    = movie["rank"]
        title   = movie["title"]
        odate   = movie["open_date"]
        aud     = movie["audience"]
        ticket  = movie["ticketing"]
        lines.append(f"{rank}위 - {title} | 개봉일: {odate} | 누적관객: {aud}명 | 예매율: {ticket}")
    # join으로 합치고, 마지막에 줄바꿈 한 번 추가
    return "\n".join(lines) + "\n"


# 5. 직접 실행 시
if __name__ == "__main__":
    result_str = get_movie_chart()
    print(result_str)
