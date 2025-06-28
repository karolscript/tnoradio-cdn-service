"""This code is to use the BunnyCDN Storage API"""

import os
from flask import jsonify
import requests
from requests.exceptions import HTTPError
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
        url=f'{self.baseUrl}/{self.bunnyStreamLibraryId}/collections?page=1&itemsPerPage=100&orderBy=date&includeThumbnails=false'
        response = requests.get(url, headers=self.headers)
        print(response.text)
        return response.text
    
    def GetVideosList(self, collection=""):
        # to build correct url
        if collection == "trailers":
            url=f'{self.baseUrl}/{self.trailersLibraryId}/videos'
        else:
            url=f'{self.baseUrl}/{self.bunnyStreamLibraryId}/videos'

        response = requests.get(url, headers=self.headers)
        print(response.text)
        return response.text
    
    def GetColletcionsList(self):
        # to build correct url
        url=f'{self.baseUrl}/{self.bunnyStreamLibraryId}/collections?page=1&itemsPerPage=500&orderBy=date&includeThumbnails=true'
        response = requests.get(url, headers=self.headers)
        return response.text
    
    def GetVideoByTitle(self, libraryId=0, title=""):
        # to build correct url
        url=f'{self.baseUrl}/{libraryId}/videos?page=1&itemsPerPage=10&search={title}&orderBy=date'
        response = requests.get(url, headers=self.headers)
        return response.text