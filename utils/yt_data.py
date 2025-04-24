# pip install google-api-python-client

from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv('/Users/jungseok/airflow/.env')

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# print(youtube)

# handle을 기준으로 channelID를 리턴하는 함수
def get_channel_id(youtube , handle):
    pass



target_handle = ''
channel_id = get_channel_id(youtube, target_handle)
print(channel_id)
