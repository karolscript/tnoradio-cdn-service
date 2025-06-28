from flask import jsonify
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

TNO_API_KEY = os.getenv('YOUTUBE_TNORADIO_API_KEY')
PROGRAMAS_API_KEY = os.getenv('YOUTUBE_API_KEY')
TNO_CHANNEL_ID = os.getenv('YOUTUBE_TNORADIO_CHANNEL_ID')
PROGRAMAS_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')


class Youtube:
    def __init__(self, channel):
        self.channel = channel
        self.api_key = TNO_API_KEY if channel == 'tnoradio' else PROGRAMAS_API_KEY
        self.channel_id = TNO_CHANNEL_ID if channel == 'tnoradio' else PROGRAMAS_CHANNEL_ID
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_playlist_items(self, playlist_name):
        playlists = self.get_playlists()
        playlist = self.find_playlist_by_name(playlists, playlist_name)

        if not playlist:
            return []  # Return an empty list if no playlist found

        playlist_items = []
        next_page_token = None

        while True:
            # Request to fetch playlist items (videos)
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist['playlist_id'],
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            # Loop through the items and add them to the list
            for item in response['items']:
                title = item['snippet']['title']
                video_id = item['snippet']['resourceId']['videoId']
                playlist_items.append({
                    'title': title, 
                    'video_id': video_id,
                    'published_at': item['snippet']['publishedAt']  # Add published date
                })

            # Check if there's another page of results
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return playlist_items

    def get_playlists(self):
        playlists = []
        next_page_token = None

        while True:
            request = self.youtube.playlists().list(
                part="snippet",
                channelId=self.channel_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            # Loop through the playlists and add them to the list
            for item in response['items']:
                title = item['snippet']['title']
                playlist_id = item['id']
                playlists.append({'title': title, 'playlist_id': playlist_id})

            # Check if there's another page of results
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return playlists

    def find_playlist_by_name(self, playlists, playlist_name):
        for playlist in playlists:
            if playlist_name.lower() in playlist['title'].lower():
                return playlist
        return None
    

    def get_all_episodes_sorted(self, playlist_name):
        all_episodes = []

        # Process episodes for both channels
        for channel in ['tnoradio', 'programas']:
            self.channel = channel
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)  # Ensure correct client for the channel

            playlists = self.get_playlists()
            playlist = self.find_playlist_by_name(playlists, playlist_name)

            if playlist:
                # Fetch playlist items
                episodes = self.get_playlist_items(playlist_name)
                print(f"Fetched {len(episodes)} episodes for {playlist_name} playlist")
                # Add video URLs and other channel-specific metadata
                for episode in episodes:
                    episode['video_url'] = f"https://www.youtube.com/watch?v={episode['video_id']}"
                    episode['channel'] = channel
                all_episodes.extend(episodes)

        # Sort all episodes by 'published_at'
        sorted_episodes = sorted(
            all_episodes,
            key=lambda x: x.get('published_at') or '',  # Default to empty string if 'published_at' is missing
        )

        return sorted_episodes
