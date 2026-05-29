import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. 目標網址
url = "https://wiki.52poke.com/zh-hant/%E6%8B%9B%E5%BC%8F%E5%88%97%E8%A1%A8"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("正在發送請求至神奇寶貝百科...")
response = requests.get(url, headers=headers)
response.encoding = "utf-8"

if response.status_code == 200:
    print("成功取得網頁內容，開始解析「所有」招式表格...")
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 使用 find_all 抓取頁面上所有帶有 'sortable' 的表格
    tables = soup.find_all("table", class_="sortable")
    
    if tables:
        moves_data = []
        print(f"偵測到網頁中共有 {len(tables)} 個符合特徵的表格，開始合併資料...")
        
        # 遍歷每一個表格
        for index, table in enumerate(tables, start=1):
            row_count = 0
            # 疊代解析當前表格的每一列資料
            for row in table.find_all("tr")[1:]:  # 跳過表頭
                cols = row.find_all("td")
                
                # 確保欄位數量足夠（通常至少要有編號、中、日、英 4 欄）
                if len(cols) >= 4:
                    move_id = cols[0].text.strip()
                    zh_name = cols[1].text.strip()
                    ja_name = cols[2].text.strip()
                    en_name = cols[3].text.strip()
                    
                    move_type = cols[4].text.strip() if len(cols) > 4 else ""
                    category = cols[5].text.strip() if len(cols) > 5 else ""
                    
                    # 避免把某些表格末尾的統計列或空列抓進來
                    # 如果編號欄位完全是空的，或是非數字相關格式，可以選擇性過濾
                    if not move_id and not zh_name:
                        continue
                        
                    moves_data.append({
                        "來源表格": f"Table_{index}",
                        "編號": move_id,
                        "中文名": zh_name,
                        "日文名": ja_name,
                        "英文名": en_name,
                        "屬性": move_type,
                        "分類": category
                    })
                    row_count += 1
            # print(f"-> 第 {index} 個表格處理完成，擷取到 {row_count} 筆招式。") # 偵錯用
        
        # 轉換成 DataFrame
        df = pd.DataFrame(moves_data)
        
        # 為了防止不同表格之間有重複抓取的招式（例如某些精選表），做個去重優化
        # 根據「中文名」或「編號」進行不重複篩選
        df_unique = df.drop_duplicates(subset=["中文名"], keep="first")
        
        # 存成 CSV
        output_csv = "pokemon_all_moves.csv"
        df_unique.to_csv(output_csv, index=False, encoding="utf-8-sig")
        
        print(f"\n🎉 全網頁抓取成功！")
        print(f"原始合併共 {len(df)} 筆，去重後最終保留 {len(df_unique)} 筆官方招式資料。")
        print(f"檔案已儲存至: {os.path.abspath(output_csv)}")
        print("\n--- 最終資料隨機 5 筆預覽 ---")
        print(df_unique.sample(5) if len(df_unique) >= 5 else df_unique.head())
        
    else:
        print("錯誤：在網頁中找不到任何帶有 class='sortable' 的表格。")
else:
    print(f"連線失敗，HTTP 狀態碼：{response.status_code}")