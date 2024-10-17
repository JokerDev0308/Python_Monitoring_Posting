import tweepy
import requests
from utils import is_within_notification_time

def post_to_sns(message):
    """Twitter と Discord にメッセージを投稿します。"""
    if is_within_notification_time():
        post_to_twitter(message)
        post_to_discord(message)

def post_to_twitter(message):
    """X (Twitter) にメッセージを投稿します。"""
    api_key = "E5lc0UPvghcCOqzjsmfz9wBoJ"
    api_secret = "LGUdBgQ2p0gEgWe8rcXSffcP4q7WOg5nXiW39iLc3NJA0lFWg6"
    access_token = "1558682332239826946-zy2UqpkxKi5MmtWsSLVz9DLq2ECvjf"
    access_token_secret = "dyuMqzYb7LDVFFnDLVfAvcC93Qi1y3QSJyyQIT30iY9JC"

    twitter = tweepy.Client(
            consumer_key        = api_key,
            consumer_secret     = api_secret,
            access_token        = access_token,
            access_token_secret = access_token_secret
            )
    

    try:
        # api.update_status(message)
        twitter.create_tweet(text = message)
        
        print("X (Twitter) への投稿に成功しました")
    except Exception as e:
        print(f"X (Twitter) への投稿に失敗しました: {e}")

def post_to_discord(message):
    """Webhook を使用して Discord にメッセージを投稿します。"""
    webhook_url = "https://discordapp.com/api/webhooks/1292843247760310347/hdK31iJZZ_LCHtv88v3HHaAsPaZxHDHi7zeFZOrX80jtv0mZVXmYl5xjsbKqlowrk8ru"
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Discord への投稿に成功しました")
        else:
            print(f"Discord への投稿に失敗しました: {response.status_code}")
    except Exception as e:
        print(f"Discord への投稿に失敗しました: {e}")


