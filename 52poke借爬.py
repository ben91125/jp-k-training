import json
import os
import re
import requests
from bs4 import BeautifulSoup

# 1. 目標網址
url = "https://wiki.52poke.com/zh-hant/%E6%8B%9B%E5%BC%8F%E5%88%97%E8%A1%A8"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# 簡易假名轉羅馬拼音對照表（確保輕量、穩定）
def kana_to_romaji(text):
    romaji_dict = {
        "あ": "a",
        "い": "i",
        "う": "u",
        "え": "e",
        "お": "o",
        "か": "ka",
        "き": "ki",
        "く": "ku",
        "け": "ke",
        "こ": "ko",
        "さ": "sa",
        "し": "shi",
        "す": "su",
        "せ": "se",
        "そ": "so",
        "た": "ta",
        "ち": "chi",
        "つ": "tsu",
        "て": "te",
        "と": "to",
        "な": "na",
        "に": "ni",
        "ぬ": "nu",
        "ね": "ne",
        "の": "no",
        "は": "ha",
        "ひ": "hi",
        "ふ": "fu",
        "へ": "he",
        "ほ": "ho",
        "ま": "ma",
        "み": "mi",
        "む": "mu",
        "め": "me",
        "も": "mo",
        "や": "ya",
        "ゆ": "yu",
        "よ": "yo",
        "ら": "ra",
        "り": "ri",
        "る": "ru",
        "れ": "re",
        "ろ": "ro",
        "わ": "wa",
        "を": "wo",
        "ん": "n",
        "が": "ga",
        "ぎ": "gi",
        "ぐ": "gu",
        "げ": "ge",
        "ご": "go",
        "ざ": "za",
        "じ": "ji",
        "ず": "zu",
        "ぜ": "ze",
        "ぞ": "zo",
        "だ": "da",
        "ぢ": "ji",
        "づ": "zu",
        "で": "de",
        "ど": "do",
        "ば": "ba",
        "び": "bi",
        "ぶ": "bu",
        "べ": "be",
        "ぼ": "bo",
        "ぱ": "pa",
        "ぴ": "pi",
        "ぷ": "pu",
        "ぺ": "pe",
        "ぽ": "po",
        "っ": "t",
        "ー": "",
        "ア": "a",
        "イ": "i",
        "ウ": "u",
        "エ": "e",
        "オ": "o",
        "カ": "ka",
        "キ": "ki",
        "ク": "ku",
        "ケ": "ke",
        "コ": "ko",
        "サ": "sa",
        "シ": "shi",
        "ス": "su",
        "セ": "se",
        "ソ": "so",
        "タ": "ta",
        "チ": "chi",
        "ツ": "tsu",
        "テ": "te",
        "ト": "to",
        "ナ": "na",
        "ニ": "ni",
        "ヌ": "nu",
        "ネ": "ne",
        "ノ": "no",
        "ハ": "ha",
        "ヒ": "hi",
        "フ": "fu",
        "ヘ": "he",
        "ホ": "ho",
        "マ": "ma",
        "ミ": "ki",
        "ム": "mu",
        "メ": "me",
        "モ": "mo",
        "ヤ": "ya",
        "ユ": "yu",
        "ヨ": "yo",
        "ラ": "ra",
        "リ": "ri",
        "ル": "ru",
        "レ": "re",
        "ロ": "ro",
        "ワ": "wa",
        "ヲ": "wo",
        "ン": "n",
    }

    # 處理坳音 (如 しょ -> sho, チュ -> chu)
    r_text = text
    yo_ons = {
        "きゃ": "kya",
        "きゅ": "kyu",
        "きょ": "kyo",
        "しゃ": "sha",
        "しゅ": "shu",
        "しょ": "sho",
        "ちゃ": "cha",
        "ちゅ": "chu",
        "ちょ": "cho",
        "にゃ": "nya",
        "にゅ": "nyu",
        "にょ": "nyo",
        "ひゃ": "hya",
        "ひゅ": "hyu",
        "ひょ": "hyo",
        "みゃ": "mya",
        "みゅ": "myu",
        "みょ": "myo",
        "りゃ": "rya",
        "りゅ": "ryu",
        "りょ": "ryo",
        "ぎゃ": "gya",
        "ぎゅ": "gyu",
        "ぎょ": "gyo",
        "じゃ": "ja",
        "じゅ": "ju",
        "じょ": "jo",
        "びゃ": "bya",
        "びゅ": "byu",
        "びょ": "byo",
        "ぴゃ": "pya",
        "ぴゅ": "pyu",
        "ぴょ": "pyo",
        "キャ": "kya",
        "キュ": "kyu",
        "キョ": "kyo",
        "シャ": "sha",
        "シュ": "shu",
        "ショ": "sho",
        "チャ": "cha",
        "チュ": "chu",
        "チョ": "cho",
        "ニャ": "nya",
        "ニュ": "nyu",
        "ニョ": "nyo",
        "ヒヤ": "hya",
        "ヒュ": "hyu",
        "ヒョ": "hyo",
        "ミャ": "mya",
        "ミュ": "myu",
        "ミョ": "myo",
        "リャ": "rya",
        "リュ": "ryu",
        "リョ": "ryo",
    }

    for k, v in yo_ons.items():
        r_text = r_text.replace(k, v)

    result = ""
    for char in r_text:
        result += romaji_dict.get(char, char)

    # 簡單清洗非英文字元與連續空格
    result = re.sub(r"[^a-zA-Z0-9\s]", "", result).lower()
    return "".join(result.split())


print("正在發送請求至神奇寶貝百科...")
response = requests.get(url, headers=headers)
response.encoding = "utf-8"

if response.status_code == 200:
    print("成功取得網頁內容，開始解析全網頁招式表格...")
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table", class_="sortable")

    if tables:
        raw_moves = []
        seen_meanings = set()

        for table in tables:
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")

                if len(cols) >= 4:
                    zh_name = cols[1].text.strip()
                    ja_name = cols[2].text.strip()
                    en_name = cols[3].text.strip()  # 英文名作為羅馬拼音備援

                    if not zh_name or not ja_name:
                        continue

                    if zh_name in seen_meanings:
                        continue
                    seen_meanings.add(zh_name)

                    # 1. 產生羅馬拼音
                    computed_romaji = kana_to_romaji(ja_name)

                    # 2. 備援防呆：如果日文名包含漢字導致轉換出來不是純英文拼音，
                    # 則直接拿第四欄的官方英文名稱處理成小寫駝峰/連字作為 romaji
                    if not computed_romaji.isalnum():
                        computed_romaji = "".join(
                            re.sub(r"[^a-zA-Z0-9\s]", "", en_name)
                            .lower()
                            .split()
                        )

                    move_item = {
                        "kanji": ja_name,
                        "kana": "",  # 大多數招式本身已是漢字混假名，留空或維持結構
                        "romaji": computed_romaji,
                        "meaning": zh_name,
                    }
                    raw_moves.append(move_item)

        # 匯出成 JSON
        output_json = "pokemon_moves_with_romaji.json"
        with open(output_json, "w", encoding="utf-8") as f:
            # 將每筆資料單獨轉成 JSON 單行字串，再用逗號與換行串接起來
            json_rows = [json.dumps(item, ensure_ascii=False) for item in raw_moves]
            f.write("[\n  " + ",\n  ".join(json_rows) + "\n]")

        print(f"\n🎉 帶有羅馬拼音的 JSON 檔案產出成功！")
        print(f"共計處理 {len(raw_moves)} 筆不重複招式。")
        print(f"檔案已儲存至: {os.path.abspath(output_json)}")

        print("\n--- 最終帶拼音之 JSON 結構預覽 ---")
        print(json.dumps(raw_moves[:3], ensure_ascii=False, indent=2))
    else:
        print("錯誤：找不到任何表格。")
else:
    print(f"連線失敗：{response.status_code}")