# pip install google-api-python-client

from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from pprint import pprint
from hdfs import InsecureClient
from datetime import datetime 
import json



load_dotenv('/Users/jungseok/airflow/.env')

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# print(youtube)

# handle을 기준으로 channelID를 리턴하는 함수
def get_channel_id(youtube , handle):
    response = youtube.channels().list(part = 'id', forHandle = handle).execute()
    return response['items'][0]['id']



target_handle = 'TimmyTrumpetTV'
channel_id = get_channel_id(youtube, target_handle)
# print(channel_id)

# channelID를 기준으로 최신영상의 ID들을 리턴하는 함수
def get_latest_video_ids(youtube, channel_id):
    response = youtube.search().list(
        # part='snippet',
        part='id',
        channelId=channel_id,
        maxResults=5,
        order='date',
    ).execute()
    video_ids = []

    for item in response['items']:
        video_ids.append(item['id']['videoId'])

    return video_ids



latest_video_ids = get_latest_video_ids(youtube, channel_id)
# pprint(latest_video_ids)


# videoId를 기준으로 comment를 리턴하는 함수
def get_comments(youtube, video_id):
    response = youtube.commentThreads().list(
        part = 'snippet',
        videoId = video_id,
        textFormat = 'plainText',
        maxResults = 100,
        order = 'relevance',
    ).execute()
    
    comments =[]

    for item in response['items']:
        comment = {
            'author' : item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
            'text' : item['snippet']['topLevelComment']['snippet']['textDisplay'],
            'publishedAt':item['snippet']['topLevelComment']['snippet']['publishedAt'],
            'likeCount':item['snippet']['topLevelComment']['snippet']['likeCount'],
            'commentId':item['snippet']['topLevelComment']['id']
        }
        comments.append(comment)

    return comments


# 구현한 함수들을 실행하여 최종 형태 리턴
def get_hadle_to_comments(youtube, handle):
    channel_id = get_channel_id(youtube, handle)
    latest_video_ids = get_latest_video_ids(youtube, channel_id)

    all_comments = {}

    for video_id in latest_video_ids:
        comments = get_comments(youtube, video_id)
        all_comments[video_id] = comments

    return {
        'hadle':handle,
        'all_comments': all_comments
    }

get_hadle_to_comments(youtube, target_handle)

def save_to_hdfs(data, path):
    client = InsecureClient('http://localhost:9870', user = 'jungseok')
    current_date = datetime.now().strftime('%y%m%d%H%M')
    file_name = f'{current_date}.json'

    # input/yt-date + 2504241144
    hdfs_path = f'{path}/{file_name}'

    json_data = json.dumps(data, ensure_ascii = False)

    with client.write(hdfs_path, encoding='utf-8') as writer:
        writer.write(json_data)

data = get_hadle_to_comments(youtube, target_handle)

save_to_hdfs(data, '/input/yt-data')