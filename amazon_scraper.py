import requests
import time
from bs4 import BeautifulSoup

async def check_stock_amazon(product_url):
    """Amazon Japanで商品の在庫状況をスクレイピングする。"""
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
 
    try:
        response = requests.get(product_url, headers=headers, timeout=200)
        #response.raise_for_status()  # リクエストが成功したか確認

        soup =  BeautifulSoup(response.content, 'html.parser')
        # 一般的な「availability」div内の在庫を確認
        availability = soup.find(id='add-to-cart-button')
        if availability != None:
            market_tag = soup.find_all(class_="offer-display-feature-text")
            if len(market_tag) > 2:
                if ("amazon" in market_tag[1].get_text().strip().lower()) and ("amazon" in market_tag[3].get_text().strip().lower()):
                    
                    sale_arr = soup.find_all(class_="a-price-whole")
                    sale = sale_arr[0].get_text().strip()

                    return {'status':"在庫あり", 'sale': sale }
                else:
                    return {'status':"在庫なし", 'sale': 0 }
            else:
                return {'status':"在庫なし", 'sale': 0 }
        else:
            return {'status':"在庫なし", 'sale': 0 }
    except requests.RequestException as e:
        print(f"商品ページの取得中にエラーが発生しました: {e}")
        return {'status':"エラー", 'sale': 0 }
