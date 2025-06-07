from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_goods(keyword):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('window-size=1920,1080')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
            """
        },
    )

    query = keyword.replace(" ", "+")
    url = f"https://www.google.com/search?tbm=shop&q={query}"

    driver.get(url)

    goods = []
    try:
        # 명시적으로 제품 리스트가 나타날 때까지 기다림 (안정적인 구조 사용)
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.sh-dlr__list-result'))
        )

        items = driver.find_elements(By.CSS_SELECTOR, 'div.sh-dlr__list-result')[:3]

        for item in items:
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, 'h3')
                price_elem = item.find_element(By.CSS_SELECTOR, 'span.a8Pemb')
                link_elem = item.find_element(By.CSS_SELECTOR, 'a.shntl')

                title = title_elem.text.strip()
                price = price_elem.text.strip()
                link = link_elem.get_attribute('href')

                goods.append({
                    'title': title,
                    'price': price,
                    'link': link
                })

            except Exception as inner_e:
                print("Inner Exception:", inner_e)
                continue

    except Exception as e:
        print("Outer Exception (Wait Error):", e)
        return []

    finally:
        driver.quit()

    return goods
