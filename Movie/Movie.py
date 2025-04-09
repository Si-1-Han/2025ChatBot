import requests
from bs4 import BeautifulSoup
import datetime
import json


with open("selectors.json", "r", encoding="utf-8") as f:
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
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
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


with open("movies_with_ticketing.json", "w", encoding="utf-8") as f:
    json.dump(movie_list, f, ensure_ascii=False, indent=2)


for movie in movie_list:
    print(f"{movie['rank']}위 | {movie['title']}")
    print(f"  개봉일    : {movie['open_date']}")
    print(f"  누적관객수: {movie['audience']}")
    print(f"  CGV 예메율 :{movie['ticketing']}")
    print("-" * 40)


