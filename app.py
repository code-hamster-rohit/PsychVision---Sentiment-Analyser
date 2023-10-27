# import os
# import json
# from flask import Flask, request, jsonify, render_template, redirect, url_for
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib import flow
# from googleapiclient.discovery import build
# import pandas as pd

# app = Flask(__name__)

# # Your client ID and client secret from the Google API Console
# CLIENT_ID = '18290753192-vpvhb7gghhm6e5gvqsgnndeg2eahnki3.apps.googleusercontent.com'
# CLIENT_SECRET = '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'

# # The OAuth 2.0 authorization flow
# OAUTH2_FLOW = flow.InstalledAppFlow.from_client_config(
#     {
#         'web': {
#             'client_id': '18290753192-vpvhb7gghhm6e5gvqsgnndeg2eahnki3.apps.googleusercontent.com',
#             'client_secret': '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',
#             'redirect_uris': ['http://localhost:5000/oauth2callback'],
#             'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
#             'token_uri': 'https://accounts.google.com/o/oauth2/token',
#         }
#     },
#     scopes=['https://www.googleapis.com/auth/youtube.force-ssl'],
# )

# # Check if an access token file exists
# ACCESS_TOKEN_FILE = 'client_secret_18290753192-vpvhb7gghhm6e5gvqsgnndeg2eahnki3.apps.googleusercontent.com.json'

# def get_credentials():
#     if os.path.exists(ACCESS_TOKEN_FILE):
#         with open(ACCESS_TOKEN_FILE, 'r') as token_file:
#             token_data = json.load(token_file)
#             print(token_data)
#         credentials = Credentials.from_authorized_user_info(**token_data)
#     else:
#         credentials = None
#     return credentials

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/login')
# def login():
#     authorization_url, _ = OAUTH2_FLOW.authorization_url()
#     return redirect(authorization_url)

# @app.route('/oauth2callback')
# def oauth2callback():
#     try:
#         OAUTH2_FLOW.fetch_token(authorization_response=request.url)
#         credentials = OAUTH2_FLOW.credentials
#         with open(ACCESS_TOKEN_FILE, 'w') as token_file:
#             json.dump(credentials.to_authorized_user_info(), token_file)

#         return redirect(url_for('api'))
#     except Exception as e:
#         return jsonify({'error': str(e)})

# @app.route('/api', methods=['POST'])
# def api():
#     try:
#         credentials = get_credentials()

#         if credentials is None or not credentials.valid:
#             return redirect(url_for('login'))

#         youtube = build('youtube', 'v3', credentials=credentials)
#         video_id = request.args.get('vid')
#         comments = []
#         results = youtube.commentThreads().list(
#             part='snippet',
#             videoId=video_id,
#             textFormat='plainText',
#         ).execute()

#         while results:
#             for item in results['items']:
#                 comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
#                 comments.append(comment)

#             # Check if there are more comments and continue iterating
#             if 'nextPageToken' in results:
#                 results = youtube.commentThreads().list(
#                     part='snippet',
#                     videoId=video_id,
#                     textFormat='plainText',
#                     pageToken=results['nextPageToken']
#                 ).execute()
#             else:
#                 break

#         df = pd.DataFrame(comments, columns=['Comment'])

#         # Return a response as JSON
#         response_data = {'message': 'Data processed successfully'}
#         return jsonify(response_data)
#     except Exception as e:
#         return jsonify({'error': str(e)})

# if __name__ == '__main__':
#     app.run(debug=True)


import os
import pandas as pd
from flask import Flask, request, render_template, jsonify
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)

# Your YouTube Data API credentials JSON file
CLIENT_SECRET_FILE = 'client_secret_383046424349-9q04579lsu7n44plh3ake4nd7fk2is99.apps.googleusercontent.com.json'
API_NAME = 'youtube'
API_VERSION = 'v3'

# Create a global variable for storing user credentials
user_credentials = None

# Initialize the YouTube Data API client
def create_youtube_service(credentials):
    return build(API_NAME, API_VERSION, credentials=credentials)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_youtube():
    video_id = request.get_json()
    video_id = video_id.split(':')[1]
    video_id = video_id[1:]
    video_id = video_id.split('"')[0]
    print(video_id)
    if not video_id:
        return jsonify({'message': 'No video URL provided'})

    global user_credentials

    if user_credentials is None:
        # Authenticate the user using OAuth 2.0
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, ['https://www.googleapis.com/auth/youtube.force-ssl'])
        user_credentials = flow.run_local_server()

    youtube_service = create_youtube_service(user_credentials)

    # Perform YouTube Data API operations here
    # For example, you can search for a video based on the video_id
    comments = []
    results = youtube_service.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
    ).execute()

    while results:
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        # Check if there are more comments and continue iterating
        if 'nextPageToken' in results:
            results = youtube_service.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                pageToken=results['nextPageToken']
            ).execute()
        else:
            break

    df = pd.DataFrame(comments, columns=['Comment'])
    df.to_csv(f'results\csv\comments_{video_id}.csv', index=False)

    json_data = df.to_json(orient='records')
    print(json_data)
    # Return a response as JSON
    response_data = {"message": "Data processed successfully", "json_data": json_data}
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
