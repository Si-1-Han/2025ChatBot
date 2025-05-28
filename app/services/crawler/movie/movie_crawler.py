# movie_crawler.py

import requests
from bs4 import BeautifulSoup
import datetime
import json
import os

def get_movie_chart():
    try:
        # selectors.json 파일 경로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        selectors_path = os.path.join(base_dir, "selectors.json")

        with open(selectors_path, "r", encoding="utf-8") as f:
            selectors = json.load(f)
        cgv_selectors = selectors["CGV"]

        kobis_api_key = "662d65ebb4eb2d7503390ff6d39f26fd"
        target_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")

        kobis_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
        params = {
            "key": kobis_api_key,
            "targetDt": target_date
        }

        res = requests.get(kobis_url, params=params)
        kobis_data = res.json()

        movie_list = []
        for movie in kobis_data['boxOfficeResult']['dailyBoxOfficeList']:
            movie_list.append({
                "rank": movie['rank'],
                "title": movie['movieNm'],
                "open_date": movie['openDt'],
                "audience": movie['audiAcc'],
                "ticketing": "N/A"
            })

        cgv_url = "http://www.cgv.co.kr/movies/?lt=1&ft=0"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/134.0.0.0 Safari/537.36"
            )
        }

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
                cgv_data[title] = ticketing

        for movie in movie_list:
            for cgv_title in cgv_data:
                if cgv_title.replace(" ", "") in movie['title'].replace(" ", ""):
                    movie['ticketing'] = cgv_data[cgv_title]
                    break

        return movie_list

    except Exception as e:
        return {"status": "error", "message": str(e)}

