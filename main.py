import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import asyncio
import logging
import time
from ttkthemes import ThemedTk
import monitor
from utils import data_field, table_field, STATUS_FILE, load_product_list, load_product_status, load_settings, save_settings
import json
import threading

# 定数
LOG_FILE = "monitor_logs.txt"  # ログファイルの場所

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),
        logging.StreamHandler() 
    ]
)


class InventoryMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自動検出と投稿")
        self.root.resizable(False, False)
        self.root.geometry("980x720")  # フルスクリーンウィンドウ
        
        self.create_ui()
        self.product_data = []  # テーブル用のデータ
        self.load_product_data()  # 保存されたファイルから既存のデータを読み込む
        self.monitoring_active = False


    def create_ui(self):
        # タイトルとヘッダー
        header_frame = tk.Frame(self.root, height=80)
        header_frame.pack(fill='x')
        header_label = tk.Label(header_frame, text="自動検出と投稿", font=("Helvetica", 24, "bold"))
        header_label.pack(pady=20)

        # 商品リストテーブル
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.create_product_table()
        
        self.upload_button = tk.Button(header_frame, text="新しいリスト", command=self.upload_product_list, bg="#4a3f9f", borderwidth=1, width=12, fg="white", font=("Helvetica", 10))
        self.upload_button.place(x=700, y=50)

        # ログエクスポートボタン
        self.export_logs_button = tk.Button(header_frame, text="作業ログ", command=self.export_logs, bg="#4a3f9f", borderwidth=1,width=12, fg="white", font=("Helvetica", 10))
        self.export_logs_button.place(x=850, y=50)

        # 監視時間のコントロール
        time_frame = tk.Frame(self.root)
        time_frame.pack(pady=20)
        
        tk.Label(time_frame, text="監視時間:", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
        
        settings = load_settings()
        self.start_time = tk.StringVar(value = settings['notification_start_time'])
        self.end_time = tk.StringVar(value = settings['notification_end_time'])
        
        tk.Entry(time_frame, textvariable=self.start_time, width=6, font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        tk.Label(time_frame, text="~", font=("Helvetica", 12)).pack(side=tk.LEFT)
        tk.Entry(time_frame, textvariable=self.end_time, width=6, font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(time_frame, text="保  存", command=self.setting_time, width=6, font=("Helvetica", 10)).pack(side=tk.LEFT, padx=5)

        # スタート/ストップボタン
        self.start_button = tk.Button(self.root, text="監視開始", command=self.start_monitoring, bg="#3f39ef",width=12, fg="white", font=("Helvetica", 10))
        self.start_button.place(x=700, y=650)
        
        self.stop_button = tk.Button(self.root, text="監視停止", command=self.stop_monitoring, bg="orange", width=12, fg="white", font=("Helvetica", 10 ))
        self.stop_button.place(x=850, y=650)
        self.stop_button.config(state=tk.DISABLED)

        # 統計表示
        self.stats_label = tk.Label(self.root, text="", font=("Helvetica", 12))
        self.stats_label.pack(pady=20)


    def create_product_table(self):
        """商品テーブルを作成し、ソート機能を追加する。"""
        columns = ["No"] + list(table_field.keys())
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings', height=15)
        # 列の定義と幅の設定
        self.tree.heading("No", text="No", command=lambda: self.sort_column("No", False))
        self.tree.column("No", anchor=tk.CENTER, width=10)  # "No"の幅を設定
        col_width = {
                'product_name': 200,
                'description': 300,
                'stock_status': 50,
                'latest_posted_date': 50,
                'affiliate_link': 150
            }
        
        for col in data_field.keys():
            if col != "product_url":
                self.tree.heading(col, text=data_field[col], command=lambda _col=col: self.sort_column(_col, False))
                self.tree.column(col, anchor=tk.W, width=col_width[col])
            else:
                pass

        # スクロールバー
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)

    def upload_product_list(self):
        """商品リストのアップロードと表示を処理する。"""
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])        
        if file_path:
            # ExcelファイルをDataFrameに読み込む
            self.product_data = pd.read_excel(file_path)            
            # 標準化された列で新しいDataFrameを作成
            standardized_columns = list(data_field.keys())            
            new_data = pd.DataFrame(columns=standardized_columns)
            for col in data_field.keys():
                    if col in self.product_data.columns:
                        new_data[col] = self.product_data[col]
            # JSON互換の辞書のリストに変換
            standardized_data = new_data.to_dict(orient='records')            
            # 新しい標準化データをJSONとして保存
            with open("product_status.json", "w") as json_file:
                json.dump(standardized_data, json_file, indent=4)
            # 商品テーブルを更新
            self.update_product_table(standardized_data)
            logging.info("商品リストをアップロードし、標準化ファイルを作成しました: %s", file_path)  # アップロードイベントをログ

    def load_product_data(self):
        """プログラム起動時に保存された商品データを読み込む。"""
        try:
            self.product_data = load_product_status()  # これがJSONから読み込むと仮定
            self.update_product_table(self.product_data)
        except FileNotFoundError:
            print("商品リストファイルが見つかりません。")
        except Exception as e:
            print(f"商品データの読み込み中にエラーが発生しました: {e}")

    def update_product_table(self, data):
        """商品データでテーブルを更新する。"""
        # 既存データをクリア
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for idx, row in enumerate(data):
            record = [idx + 1] + [row.get(col) for col in table_field.keys()]
            self.tree.insert("", "end", values=tuple(record))

    def sort_column(self, col, reverse):
        """列によってテーブルをソートする。"""        
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]        
        def try_parse(value):
            try:
                return float(value)
            except ValueError:
                return value  
        # ソートされたリストを使用してアイテムを並べ替え
        l.sort(key=lambda x: try_parse(x[0]), reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        # 次回のために逆ソートに設定
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse)) 

    def start_monitoring(self):
        """商品の監視を開始する。"""
        logging.info("監視開始。")
        global monitoring
        monitoring = True
        # 監視を別スレッドで実行
        thread = threading.Thread(target= self.is_monitoring)
        thread.start() 
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.upload_button.config(state=tk.DISABLED)
        self.export_logs_button.config(state=tk.DISABLED)
            
    def stop_monitoring(self):
        """商品の監視を停止する。"""
        logging.info("監視停止。")  # 監視停止イベントをログ
        global monitoring
        monitoring = False                 
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.upload_button.config(state=tk.NORMAL)
        self.export_logs_button.config(state=tk.NORMAL)
            
    def is_monitoring(self):
        products = load_product_list(STATUS_FILE)
        records  = self.tree.get_children()
        while monitoring:
            for idx, product in enumerate(products):
                if idx != 0:
                    prev_idx = idx-1
                else:
                    prev_idx = len(products)-1

                if monitoring:   
                    self.realtime_record(prev_idx,records[prev_idx],False)
                    self.realtime_record(idx,records[idx],True)
                    asyncio.run(monitor.check_and_post_stock(product, idx))
                else:
                    self.realtime_record(prev_idx,records[prev_idx],True)
                    return
            time.sleep(60)

    def realtime_record(self, idx, record_id, point):
        products_list = load_product_status()
        product = products_list[idx]
        product['stock_status'] = ">>> モニタリング..." if point else product['stock_status']

        prev_record = [idx+1] + [product.get(col) for col in table_field.keys()]
        self.tree.item(record_id, values=tuple(prev_record))

    
    def setting_time(self):
        settings = load_settings()
        settings["notification_start_time"] = self.start_time.get()
        settings["notification_end_time"] = self.end_time.get()
        save_settings(settings)

    def export_logs(self):
        """ログをファイルにエクスポートする。"""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("テキストファイル", "*.txt"), ("CSVファイル", "*.csv")])
        if file_path:
            with open(LOG_FILE, "r") as log_file:
                log_data = log_file.read()
            with open(file_path, "w") as output_file:
                output_file.write(log_data)
            logging.info("==========>ログをエクスポートしました: %s <=============", file_path)  # エクスポートイベントをログ

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # モダンテーマを使用
    app = InventoryMonitorApp(root)
    root.mainloop()
