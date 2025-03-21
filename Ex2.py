import requests
from bs4 import BeautifulSoup

response = requests.get("https://startcoding.pythonanywhere.com/basic")
html = response.text
soup = BeautifulSoup(html, 'html.parser')
items = soup.select(".product")
for item in items:
    category = item.select_one(".product-category").text
    name = item.select_one(".product-name").text
    link = item.select_one(".product-name > a").attrs['href']
    price = item.select_one(".product-price").text.split('원')[0].replace(',', '')
    print(category, name, link, price)
