from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

app = Flask(__name__)

@app.route("/운세/<zodiac>", methods=["GET"])
def get_fortune(zodiac):
    try:
        # 네이버 검색 URL 생성
        query = urllib.parse.quote(f"{zodiac} 운세")
        url = f"https://search.naver.com/search.naver?query={query}"
        headers = {"User-Agent": "Mozilla/5.0"}

        # 페이지 요청
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # 종합 운세 추출
        fortune_elem = soup.select_one(".detail_box") or soup.select_one(".text._cs_fortune_text")
        fortune = fortune_elem.get_text(strip=True) if fortune_elem else "운세를 찾을 수 없습니다."

        # 연령별 운세 추출 (구조 유연하게 대응)
        age_elems = soup.select("ul.list_age li")
        ages = []

        for age_elem in age_elems:
            age_title = age_elem.select_one(".age") or age_elem.select_one("strong")
            age_desc = age_elem.select_one(".text") or age_elem.select_one("span")

            if age_title and age_desc:
                ages.append({
                    "age": age_title.get_text(strip=True),
                    "fortune": age_desc.get_text(strip=True)
                })

        return jsonify({
            "zodiac": zodiac,
            "fortune": fortune,
            "ages": ages
        })

    except Exception as e:
        return jsonify({
            "zodiac": zodiac,
            "fortune": f"오류 발생: {str(e)}",
            "ages": []
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
