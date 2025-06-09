import requests
from bs4 import BeautifulSoup

def get_stock():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    url = 'https://finance.naver.com/sise/sise_quant.naver'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    stock = []
    table = soup.find('table', class_='type_2')
    rows = table.find_all('tr')[2:7]  # 상위 5개 행만 추출

    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 1:
            stock_name = cols[1].text.strip()
            current_price = cols[2].text.strip()
            price_change = cols[3].text.strip()
            rate_change = cols[4].text.strip()
            volume = cols[5].text.strip()
            trade_amount = cols[6].text.strip()

            stock.append({
                'name': stock_name,
                'current_price': current_price,
                'price_change': price_change,
                'rate_change': rate_change,
                'volume': volume,
                'trade_amount': trade_amount
            })

    return stock
