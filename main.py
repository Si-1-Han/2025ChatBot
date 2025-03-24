import requests as req
from bs4 import BeautifulSoup as bs

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

res = req.get("http://finance.naver.com/sise/sise_quant.naver", headers=headers)
soup = bs(res.text, "lxml")

# soup 데이터에서 필요한 요소 검색하기
title = soup.select("a.tltle")
price = soup.select("td.number:nth-child(3)")
volume = soup.select("td.number:nth-child(6)")

# 리스트의 데이터 길이를 확인해서 검증(len())

min_len = min(len(title), len(price), len(volume))

for i in range(min_len):
    print(f"{title[i].get_text(strip=True)}: {price[i].get_text(strip=True)}원, 거래량 {volume[i].get_text(strip=True)}주")
