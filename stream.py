"""This code is to use the BunnyCDN Storage API"""

import os
import json
from flask import jsonify
import requests
from requests.exceptions import HTTPError, RequestException
from urllib import parse
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

API_KEY = os.getenv('BUNNY_API_KEY') 

class Stream:
    def __init__(self):
        self.baseUrl = "https://video.bunnycdn.com/library"
        self.headers = {
            "accept": "application/json",
            "AccessKey": API_KEY,
            'Content-Type': 'application/json',
        }
        self.bunnyStreamLibraryId = 286671
        self.trailersLibraryId = 286671     

    def GetVideoLibraryList(self):
        try:
            url=f'{self.baseUrl}/{self.bunnyStreamLibraryId}/collections?page=1&itemsPerPage=100&orderBy=date&includeThumbnails=false'
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"Error in GetVideoLibraryList: {e}")
            return {"error": str(e), "items": []}
    
    def GetVideosList(self, collection=""):
        try:
            # to build correct url
            if collection == "trailers":
                url=f'{self.baseUrl}/{self.trailersLibraryId}/videos'
            else:
                url=f'{self.baseUrl}/{self.bunnyStreamLibraryId}/videos'

            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            print(f"Successfully fetched {len(data.get('items', []))} videos for collection: {collection}")
            return data
            
        except RequestException as e:
            print(f"Error in GetVideosList: {e}")
            return {"error": str(e), "items": [], "totalItems": 0}
    
    def GetColletcionsList(self):
        try:
            # to build correct url
            url=f'{self.baseUrl}/{self.bunnyStreamLibraryId}/collections?page=1&itemsPerPage=500&orderBy=date&includeThumbnails=true'
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"Error in GetColletcionsList: {e}")
            return {"error": str(e), "items": []}
    
    def GetVideoByTitle(self, libraryId=0, title=""):
        try:
            # to build correct url
            url=f'{self.baseUrl}/{libraryId}/videos?page=1&itemsPerPage=10&search={title}&orderBy=date'
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"Error in GetVideoByTitle: {e}")
            return {"error": str(e), "items": []}