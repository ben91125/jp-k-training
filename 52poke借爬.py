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
        "ぐ": "ぐ",
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
        "ぼ": "bo",
        "っ": "t",
        "ー": "-",
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
        "ぬ": "nu",
        "ネ": "ne",
        "ノ": "no",
        "ハ": "ha",
        "ヒ": "hi",
        "フ": "fu",
        "ヘ": "he",
        "ホ": "ho",
        "マ": "ma",
        "ミ": "mi",
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
    result = "".join([romaji_dict.get(char, char) for char in r_text])
    result = re.sub(r"[^a-zA-Z0-9\s-]", "", result).lower()
    return "".join(result.split())


print("正在發送請求至神奇寶貝百科...")
response = requests.get(url, headers=headers)
response.encoding = "utf-8"

if response.status_code == 200:
    print("成功取得網頁內容，開始進行高級資料清洗與分離...")
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
                    ja_td = cols[2]
                    en_name = cols[3].text.strip()

                    if not zh_name or not ja_td.text.strip():
                        continue

                    if zh_name in seen_meanings:
                        continue
                    seen_meanings.add(zh_name)

                    # --- 核心邏輯：從 Ruby 標籤提取 漢字(kanji) 與 純假名(kana) ---
                    ruby_tag = ja_td.find("ruby")

                    if ruby_tag:
                        # 1. 提取完整的漢字招式名（要把 <rt> 標籤內的小字拿掉，留下原本網頁上顯示的大字）
                        # 複製一個節點避免破壞原本結構
                        kanji_soup = BeautifulSoup(str(ruby_tag), "html.parser")
                        for rt in kanji_soup.find_all("rt"):
                            rt.decompose()  # 拔除注音小字
                        kanji_name = kanji_soup.get_text().strip()

                        # 2. 提取純假名（把漢字丟掉，只留下 <rt> 裡的平假名，以及 ruby 之外的片假名外來語）
                        kana_soup = BeautifulSoup(str(ruby_tag), "html.parser")
                        parts = []
                        for child in (
                            kana_soup.find("ruby").contents
                            if kana_soup.find("ruby")
                            else []
                        ):
                            if child.name == "rt":
                                parts.append(child.get_text().strip())
                            elif child.name is None:  # 這是 ruby 內部的純片假名或符號
                                parts.append(str(child).strip())
                        pure_kana = "".join(parts)

                        # 結合 ruby 之外可能殘留的片假名（例如：連続パンチ 中的 パンチ）
                        # 我們直接用完整文字扣除掉 ruby 漢字，補上假名即可。這裡採用最穩定的做法：
                        # 如果純假名長度怪怪的，就用原本整欄未清洗的文字做對照
                        if not pure_kana:
                            pure_kana = ja_td.text.strip()
                    else:
                        # 如果這招本來就全是平假名/片假名（沒漢字），那 kanji 和 kana 就一樣
                        kanji_name = ja_td.text.strip()
                        pure_kana = ja_td.text.strip()

                    # 3. 基於純假名（kana）計算羅馬拼音
                    computed_romaji = kana_to_romaji(pure_kana)

                    # 備援防呆：若轉換失敗有雜質，用官方英文名稱代替
                    if not computed_romaji.replace("-", "").isalnum():
                        computed_romaji = "".join(
                            re.sub(r"[^a-zA-Z0-9\s]", "", en_name)
                            .lower()
                            .split()
                        )

                    # 封裝成你要求的新結構
                    move_item = {
                        "kanji": kanji_name,
                        "kana": pure_kana,
                        "romaji": computed_romaji,
                        "meaning": zh_name,
                    }
                    raw_moves.append(move_item)

        # 4. 匯出成 JSON (優化：一筆招式剛好佔一列)
        output_json = "pokemon_moves_perfect.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json_rows = [
                json.dumps(item, ensure_ascii=False) for item in raw_moves
            ]
            f.write("[\n  " + ",\n  ".join(json_rows) + "\n]")

        print(f"\n🎉 完美版 JSON 檔案產出成功！")
        print(f"共計處理 {len(raw_moves)} 筆不重複招式。")
        print(f"檔案已儲存至: {os.path.abspath(output_json)}")

        print("\n--- 最終完美版 JSON 結構預覽 ---")
        print(json.dumps(raw_moves[:3], ensure_ascii=False, indent=2))
    else:
        print("錯誤：找不到任何表格。")
else:
    print(f"連線失敗：{response.status_code}")