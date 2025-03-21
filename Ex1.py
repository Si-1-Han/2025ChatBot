import requests
from bs4 import BeautifulSoup

response = requests.get("https://startcoding.pythonanywhere.com/basic")
html = response.text
soup = BeautifulSoup(html, 'html.parser')
category = soup.select_one(".product-category").text
name = soup.select_one(".product-name").text
link = soup.select_one(".product-name > a").attrs['href']
price = soup.select_one(".product-price").text.strip().replace(',', '').replace('원', '')

print(category, name, link, price)