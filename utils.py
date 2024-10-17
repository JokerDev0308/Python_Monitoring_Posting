import json
import os
from datetime import datetime

SETTINGS_FILE = 'settings.json'
STATUS_FILE = "product_status.json"

# キーとデフォルト表示名を定義
data_field = {
    'product_name': '商  品  名',
    'description': "説     明",
    'product_url': "商 品 URL",
    'stock_status': '在庫状況',
    'latest_posted_date': '最新投稿日',
    'affiliate_link': 'アフィリエイト'
}

table_field = data_field.copy()
table_field.pop('product_url')

def load_product_list(product_file):
    """JSONファイルから商品リストを読み込む。"""
    with open(product_file, 'r',encoding='utf-8') as file:
        return json.load(file)

def load_settings():
    """JSONファイルから設定を読み込む。"""
    try:
        with open(SETTINGS_FILE, 'r',encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            'notification_start_time': '00:00',
            'notification_end_time': '23:59'
        }

def save_settings(settings):
    """設定をJSONファイルに保存する。"""
    with open(SETTINGS_FILE, 'w',encoding='utf-8') as file:
        json.dump(settings, file,ensure_ascii=False, indent=4)

# 商品ステータスデータを読み込む（存在しない場合はファイルを作成）
def load_product_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r',encoding='utf-8') as file:
            return json.load(file)
    else:
        # キーを持つ空のファイルを初期化
        with open(STATUS_FILE, 'w',encoding='utf-8') as file:
            json.dump([], file,ensure_ascii=False,)  # 空のJSON配列を作成
        return []

# 更新された商品ステータスをファイルに保存
async def save_product_status(product_status):
    with open(STATUS_FILE, 'w',encoding='utf-8') as file:
        json.dump(product_status, file,ensure_ascii=False, indent=4)

# 新しい商品リストがアップロードされたときに商品ステータスを更新
async def update_product_status(new_product_list_path):
    new_products = load_product_list(new_product_list_path)

    # 既存の商品のステータスを読み込む
    product_status = load_product_status()

    # 新しい商品を商品ステータスにマージ
    for row in new_products:
        product_url = row['product_url']
        existing_product = next((item for item in product_status if item['product_url'] == product_url), None)
        
        if existing_product:
            # 既存の商品を更新
            existing_product['stock_status'] = row['stock_status']
            existing_product['affiliate_link'] = row['affiliate_link']
        else:
            # 新しい商品を追加
            new_entry = {
                'product_name': row['product_name'],
                'description': row['description'],
                'product_url': product_url,
                'stock_status': row['stock_status'],
                'latest_posted_date': None,  # 初期値は投稿日なし
                'affiliate_link': row['affiliate_link']
            }
            product_status.append(new_entry)

    # 更新された商品ステータスをファイルに保存
    await save_product_status(product_status)

def is_within_notification_time():
    """現在の時刻が通知時間のウィンドウ内かチェックする。"""
    settings = load_settings()
    current_time = datetime.now().time()
    start_time = datetime.strptime(settings['notification_start_time'], "%H:%M").time()
    end_time = datetime.strptime(settings['notification_end_time'], "%H:%M").time()

    return start_time <= current_time <= end_time
