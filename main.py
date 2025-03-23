import requests as req
from bs4 import BeautifulSoup as bs

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

res = req.get("http://finance.naver.com/sise/sise_quant.naver", headers=headers)
soup = bs(res.text, "lxml")

# soup 데이터에서 필요한 요소 검색하기
title = soup.select("a.tltle")
price = soup.select("td.number:n")

# 리스트의 데이터 길이를 확인해서 검증(len())
print(len(price))

#
#contentarea > div.box_type_l > table > tbody > tr:nth-child(3) > td:nth-child(3)