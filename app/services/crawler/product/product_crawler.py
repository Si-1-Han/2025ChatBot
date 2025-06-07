import requests
from bs4 import BeautifulSoup

def get_goods(user_message):
    url = f'https://www.coupang.com/np/search?q={user_message}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    goods = []
    for item in soup.select('.search-product')[:3]:
        title = item.select_one('.name').get_text(strip=True)
        price = item.select_one('.price-value').get_text(strip=True)
        link = 'https://www.coupang.com' + item.find('a')['href']
        goods.append({"title": title, "price": price, "link": link})

    return goods