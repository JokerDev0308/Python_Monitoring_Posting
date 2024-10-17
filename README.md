# **Amazon 在庫モニター X（Twitter）＆Discord通知機能付き**

このプロジェクトは、**Amazon** での商品在庫状況を監視し、在庫ステータスを **X（旧Twitter）** や **Discord** に自動で通知します。監視対象の製品は **Excel（XLSX）** ファイルを通じて管理し、通知は指定された時間内にのみ送信され、重複投稿を回避します。

### **機能:**
- **Amazon スクレイピング**: Amazon（amazon.co.jp）の商品在庫状況を直接スクレイピング。
- **SNS通知**: 在庫状況をX（Twitter）とDiscordに通知。DiscordにはWebhookを利用。
- **重複投稿の回避**: 在庫状況が変わった場合のみ通知（例: 「在庫なし」から「在庫あり」への変更）。
- **時間指定通知**: 通知を送信する時間帯を指定可能。
- **GUIインターフェース**: ユーザーフレンドリーなGUI（Tkinter）で、商品リストのアップロードや監視の開始/停止、設定の変更が可能。
- **Excel（XLSX）統合**: 監視対象の製品データ（名前、URL、アフィリエイトリンク）はExcelファイルで管理。

---

## **プロジェクト構成**

```plaintext
inventory_monitor/
│
├── main.py                    # GUI付きメインエントリーポイント
├── monitor.py                 # 在庫監視とSNS通知ロジック
├── amazon_scraper.py           # Amazon商品の在庫スクレイパー
├── sns_posting.py             # X（Twitter）およびDiscordへの通知ロジック
├── utils.py                   # ユーティリティ関数（設定読み込み、時間チェックなど）
├── product_list.xlsx          # 製品データが含まれるExcelファイル
├── product_status.json        # 商品在庫ステータスを保存するファイル
├── requirements.txt           # 必要なPythonライブラリ
├── README.md                  # プロジェクトドキュメント（このファイル）
```

## for bulding
``` bash
  pyinstaller -F --noconsole --onefile --icon=my.ico --add-data "settings.json;." --add-data "product_status.json;." --paths=C:\Users\Joker\myenv\Lib\site-packages main.py
```

## for building test
  pyinstaller -F --paths=C:\Users\Joker\myenv\Lib\site-packages main.py

---

## **必要条件**

- **Python 3.x**
- **Pip**（Pythonパッケージ管理ツール）

### **Pythonライブラリ**
`requirements.txt`ファイルにリストされたライブラリをインストールしてください。以下のコマンドでインストールできます。

```bash
pip install -r requirements.txt
```

このプロジェクトで使用されるライブラリは次の通りです：
- `tweepy`: X（Twitter）への投稿
- `requests`: HTTPリクエスト送信（Discord Webhookに使用）
- `pandas`: Excel（XLSX）ファイルの処理
- `openpyxl`: Excel（XLSX）ファイルの読み取り
- `beautifulsoup4`: Amazonのスクレイピング

---

## **セットアップ**

### **1. API認証情報の設定**

#### **X（Twitter）APIの設定:**
- **Twitter Developer Account** を作成し、次のAPIキーを取得してください：
  - API Key
  - API Secret
  - Access Token
  - Access Token Secret

これらのAPIキーは **GUI** から設定するか、直接 `settings.json` ファイルで指定できます。

#### **Discord Webhookの設定:**
- **Discord Webhook URL** を作成します：
  - Discordサーバーに移動します。
  - 新しいチャンネルを作成するか、既存のチャンネルを使用します。
  - `チャンネル設定` -> `統合` -> `Webhook` に移動し、Webhookを作成します。
  - **Webhook URL** をコピーし、**GUI** または `settings.json` ファイルに設定します。

---

## **使用方法**

### **1. アプリケーションの起動**
`main.py` ファイルを実行して、アプリケーションを開始します。

```bash
python main.py
```

これにより、GUIインターフェースが開き、設定の変更、商品リストのアップロード、および監視の開始/停止が可能になります。

### **2. GUIの使用**

- **商品リスト（XLSX）のアップロード**:
  - 「Upload Product List (XLSX)」ボタンをクリックして、Excelファイル (`product_list.xlsx`) をアップロードします。
  - Excelファイルには、次の列を含める必要があります：`product_name`, `product_url`, `affiliate_url`。

- **監視の開始/停止**:
  - 商品リストをアップロードした後、「Start Monitoring」ボタンをクリックして、商品の在庫状況の監視を開始します。監視は60秒ごとに行われます。
  - 「Stop Monitoring」ボタンをクリックして、監視を停止できます。

- **通知時間の設定**:
  - 通知を送信する時間帯を、`HH:MM`形式で開始時間と終了時間を設定できます。通知はこの時間帯のみ送信されます。

- **設定の保存**:
  - 通知時間やAPIキーなどの設定を変更した後、「Save Settings」ボタンをクリックして、`settings.json`に保存します。

---

## **Excelファイル形式（XLSX）**

商品データは、`product_list.xlsx` というExcelファイルで管理されます。次の列を含める必要があります：

| 列名             | 説明                                                      |
|------------------|------------------------------------------------------------|
| `product_name`   | 商品名。                                                   |
| `product_url`    | Amazonの商品URL。                                     |
| `affiliate_url`  | 在庫がある場合に投稿するアフィリエイトURL。                 |

#### **`product_list.xlsx` の例**:

| product_name     | product_url                                           | affiliate_url                        |
|------------------|-------------------------------------------------------|--------------------------------------|
| Product 1        | https://www.amazon.co.jp/dp/B08CFSZLQ4                | https://www.amazon.co.jp/dp/B08CFSZLQ4?tag=affiliateid |
| Product 2        | https://www.amazon.co.jp/dp/B07XJ8C8F5                | https://www.amazon.co.jp/dp/B07XJ8C8F5?tag=affiliateid |

---

## **通知の制御**

### **重複通知の回避**:
- システムは、在庫状況が変わった場合のみX（Twitter）およびDiscordに通知します（例: 「在庫なし」から「在庫あり」への変更）。
- 商品の在庫状況が「在庫あり」や「在庫なし」のままであれば、追加の通知は送信されません。

### **時間指定通知**:
- 通知は、ユーザーが指定した時間帯内でのみ送信されます（例: `09:00` から `17:00` の間）。
- この時間帯は、GUIを使用して設定するか、`settings.json` ファイルを直接編集して設定できます。

---

## **設定ファイル（`settings.json`）**

アプリケーションの設定は、`settings.json` ファイルに保存されます。これには次の情報が含まれます：
- 通知時間（開始時間と終了時間）。
- Twitter（X）APIの認証情報。
- Discord Webhook URL。

#### **`settings.json` の例**:

```json
{
    "notification_start_time": "09:00",
    "notification_end_time": "17:00",
    "twitter_api_key": "your_twitter_api_key",
    "twitter_api_secret": "your_twitter_api_secret",
    "twitter_access_token": "your_twitter_access_token",
    "twitter_access_token_secret": "your_twitter_access_token_secret",
    "discord_webhook_url": "your_discord_webhook_url"
}
```

---

## **商品ステータスの永続化（`product_status.json`）**

各商品の在庫状況は、`product_status.json` ファイルに保存されます。これにより、システムは前回の在庫ステータスを記憶し、アプリケーションを再起動しても重複通知を防ぐことができます。

---

## **貢献**

このプロジェクトへの貢献や改善提案を歓迎します。プルリクエストを作成するか、イシューをオープンしてください。

---

## **ライセンス**

このプロジェクトはMITライセンスの下でライセンスされています。

---

## **連絡先**

問題、質問、または提案がある場合は、プロジェクト所有者にご連絡ください。

---

この**README**は、セットアップと使用方法を簡単に理解できるように設計されています。もし修正や追加の説明が必要であればお知らせください！