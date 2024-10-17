import time
import asyncio
from amazon_scraper import check_stock_amazon
from sns_posting import post_to_sns
from datetime import datetime
from utils import load_product_list, STATUS_FILE, load_product_list, is_within_notification_time, load_product_status, save_product_status

# グローバル変数: モニタリングループの制御
monitoring = False

def is_monitoring():
    """JSONファイルにリストされている商品の在庫を監視し始める。"""
    global monitoring
    monitoring = True

    # JSONファイルから商品リストを読み込む
    products = load_product_list(STATUS_FILE)

    while monitoring:
        for idx, product in enumerate(products):
            asyncio.run(check_and_post_stock(product, idx))
        #time.sleep(60)  # 60秒ごとにチェック

def stop_monitoring():
    """監視プロセスを停止する。"""
    global monitoring
    monitoring = False

async def check_and_post_stock(product, idx):
    """在庫状況をチェックし、変化があればSNSに投稿する。"""
    product_name = product['product_name']
    description = product['description']
    product_url = product['product_url']
    affiliate_link = product['affiliate_link']

    product_status = load_product_status()
    # Amazon Japanでの在庫状況をチェック
    stock_data = await check_stock_amazon(product_url)
    current_status = stock_data['status']
    # 商品が見つからなければ「不明」とみなす
    # previous_status = product_status[idx]['stock_status']

    # 在庫状況が変わった場合、SNSに投稿
    # if previous_status != current_status:
    product_status[idx]['stock_status'] = current_status
    
    if current_status == "在庫あり" and is_within_notification_time():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"💡在庫復活💡PR\n  {current_time}\n {product_name}\n {stock_data['sale']}円\n { f'{description}\n' if description.lower() != "nan" else "" }  {affiliate_link}"
        post_to_sns(message)
        product_status[idx]['latest_posted_date'] = current_time
    elif current_status == "在庫なし":
        print(f"{product_name} は在庫がありません。")
    
    await save_product_status(product_status)
    # else:
    #     pass

