import requests
import datetime
from collections import defaultdict

def get_weather():
    now = datetime.datetime.now()
    today_str = now.strftime("%Y%m%d")
    tomorrow = now + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y%m%d")

    # 3시간 발표시각 리스트(가장 최근 시각부터 차례로 시도)
    base_times = [23, 20, 17, 14, 11, 8, 5, 2]
    found = False

    for t in base_times:
        if now.hour >= t:
            base_time = f"{t:02}00"
            base_date = today_str
        else:
            # 새벽 1시 이전이면 전날 데이터가 최신일 수 있음
            base_time = "2300"
            base_date = (now - datetime.timedelta(days=1)).strftime("%Y%m%d")
        print("base_date:", base_date, "base_time:", base_time)
        params = {
            'serviceKey': 'n6NfI6+c9wxnu4k+3eCNMIAOGYQIoPxLXMjucAYt7X89SZUkXNV3nlC8g0bjJ1ZnofFB7ClDBiYXbmH9hYHBvg==',
            'pageNo': '1',
            'numOfRows': '1000',
            'dataType': 'JSON',
            'base_date': base_date,
            'base_time': base_time,
            'nx': '60',
            'ny': '127'
        }
        url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
        response = requests.get(url, params=params)
        print("응답 텍스트:", response.text[:100])
        try:
            items = response.json()['response']['body']['items']['item']
            found = True
            break
        except Exception:
            continue

    if not found:
        print("데이터가 없습니다.")
        return {}

    # 이하 동일
    by_date = defaultdict(lambda: defaultdict(dict))
    for item in items:
        fcstDate = item['fcstDate']
        fcstTime = item['fcstTime']
        category = item['category']
        value = item['fcstValue']
        by_date[fcstDate][fcstTime][category] = value

    def extract_summary(date_dict):
        summary = {}
        for t, info in date_dict.items():
            if 'TMN' in info:
                summary['최저기온'] = info['TMN']
            if 'TMX' in info:
                summary['최고기온'] = info['TMX']
        for main_time in ["0900", "1200", "1500"]:
            if main_time in date_dict:
                info = date_dict[main_time]
                if 'TMP' in info:
                    summary[f"{main_time}시기온"] = info['TMP']
                if 'POP' in info:
                    summary[f"{main_time}시강수확률"] = info['POP']
                if 'SKY' in info:
                    sky_map = {"1": "맑음", "3": "구름많음", "4": "흐림"}
                    summary[f"{main_time}시하늘"] = sky_map.get(str(info['SKY']), str(info['SKY']))
        return summary

    today_summary = extract_summary(by_date.get(today_str, {}))
    tomorrow_summary = extract_summary(by_date.get(tomorrow_str, {}))

    print("▶ 오늘 요약")
    for k, v in today_summary.items():
        print(f"{k}: {v}")
    print("\n▶ 내일 요약")
    for k, v in tomorrow_summary.items():
        print(f"{k}: {v}")

    return {"today": today_summary, "tomorrow": tomorrow_summary}

if __name__ == "__main__":
    get_weather()
