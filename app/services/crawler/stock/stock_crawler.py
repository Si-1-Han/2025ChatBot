import requests
from bs4 import BeautifulSoup

def get_stock():
    url = 'http://finance.naver.com/sise/sise_quant.naver'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    stock = []
    for row in soup.select('table.type_2 tbody tr')[:10]:
        cols = row.select('td')
        if len(cols) >= 2:
            name = cols[0].get_text(strip=True)
            price = cols[1].get_text(strip=True)
            stock.append({"name": name, "price": price})

    return stock