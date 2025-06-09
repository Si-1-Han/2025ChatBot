import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver

def get_goods(user_message):
    url = f"https://search.11st.co.kr/pc/total-search?kwd={user_message}"
    driver = webdriver.Chrome()
    try:
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.c-card-item"))
        )

        products = driver.find_elements(By.CSS_SELECTOR, "div.c-card-item")

        result = []
        for product in products[:5]:
            try:
                title = product.find_element(By.CSS_SELECTOR, ".c-card-item__name dd").text
            except NoSuchElementException:
                title = "상품명 없음"

            try:
                price = product.find_element(By.CSS_SELECTOR, ".c-card-item__price .value").text
            except NoSuchElementException:
                price = "가격 정보 없음"

            try:
                rating = product.find_element(By.CSS_SELECTOR, ".c-starrate__text").text
            except NoSuchElementException:
                rating = "평점 정보 없음"

            try:
                link = product.find_element(By.CSS_SELECTOR, "a.c-card-item__anchor").get_attribute('href')
            except NoSuchElementException:
                link = "링크 정보 없음"

            item = {
                'title': title,
                'price': price,
                'rating': rating,
                'link': link,
            }
            result.append(item)

        return result

    except TimeoutException:
        print("요청 시간이 초과되었습니다.")
        return []

    finally:
        driver.quit()
