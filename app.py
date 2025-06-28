from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from storage import Storage
from stream import Stream
from youtube import Youtube
import os
import logging
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
CORS(app)
logger = logging.getLogger()
logger.setLevel("INFO")

app.app_context().push()

STORAGE_API_KEY = os.environ.get("BUNNY_STORAGE_API_KEY")

@app.route("/health")
def hello_world():
    return "<p>Hello, World!</p>"

# Nuevos endpoints para upload a Bunny.net
@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        # Obtener parámetros del request
        show_slug = request.form.get('show_slug')
        image_type = request.form.get('image_type')
        file = request.files.get('file')
        
        if not all([show_slug, image_type, file]):
            return jsonify({"error": "Missing required parameters: show_slug, image_type, file"}), 400
        
        # Crear instancia de Storage
        myStorage = Storage(STORAGE_API_KEY, "shows-tnoradio", show_slug)
        
        # Construir la ruta de almacenamiento
        storage_path = f"{image_type}/{file.filename}"
        
        # Guardar archivo temporalmente
        temp_path = f"/tmp/{file.filename}"
        file.save(temp_path)
        
        # Subir a Bunny.net
        result = myStorage.PutFile(
            file_name=file.filename,
            storage_path=storage_path,
            local_upload_file_path="/tmp"
        )
        
        # Limpiar archivo temporal
        os.remove(temp_path)
        
        if result.get("status") == "success":
            return jsonify({
                "status": "success",
                "message": "File uploaded successfully to Bunny.net",
                "file_path": storage_path
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": result.get("msg", "Upload failed")
            }), 500
            
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/delete_file', methods=['DELETE'])
def delete_file():
    try:
        show_slug = request.args.get('show_slug')
        image_type = request.args.get('image_type')
        filename = request.args.get('filename')
        
        if not all([show_slug, image_type, filename]):
            return jsonify({"error": "Missing required parameters: show_slug, image_type, filename"}), 400
        
        # Crear instancia de Storage
        myStorage = Storage(STORAGE_API_KEY, "shows-tnoradio", show_slug)
        
        # Construir la ruta del archivo
        storage_path = f"{image_type}/{filename}"
        
        # Eliminar archivo
        result = myStorage.DeleteFile(storage_path)
        
        if result.get("status") == "success":
            return jsonify({
                "status": "success",
                "message": "File deleted successfully from Bunny.net"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": result.get("msg", "Delete failed")
            }), 500
            
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        show_slug = request.args.get('show_slug')
        image_type = request.args.get('image_type')
        
        if not show_slug:
            return jsonify({"error": "Missing required parameter: show_slug"}), 400
        
        # Crear instancia de Storage
        myStorage = Storage(STORAGE_API_KEY, "shows-tnoradio", show_slug)
        
        # Listar archivos
        if image_type:
            result = myStorage.GetStoragedObjectsList(image_type)
        else:
            result = myStorage.GetStoragedObjectsList()
        
        return jsonify({
            "status": "success",
            "files": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_stream',  methods=['GET'])
def get_stream():
    try:
        myStream = Stream()
        theList = myStream.GetVideoLibraryList()
        return theList
    except Exception as e:
        print(e)
        return jsonify("hubo error")

@app.route('/get_videos',  methods=['GET'])
def get_videos():
    try:
        stream = request.args.get('collection')
        myStream = Stream()
        theList = myStream.GetVideosList(stream)
        return theList
    except Exception as e:
        print(e)
        return jsonify("hubo error")
    
@app.route('/get_video_by_title',  methods=['GET'])
def get_video_by_title():
    try:
        title = request.args.get('title')
        libraryId = request.args.get('libraryId')
        myStream = Stream()
        theVideo = myStream.GetVideoByTitle(libraryId,title)
        return theVideo
    except Exception as e:
        print(e)
        return jsonify("hubo error trayendo el video")

@app.route('/get_stream_collections',  methods=['GET'])
def get_collections_list():
    try:
        myStream = Stream()
        theList = myStream.GetColletcionsList()
        return theList
    except Exception as e:
        print(e)
        return jsonify("hubo error")

@app.route('/get_shows',  methods=['GET'])
def get_shows():
    show_slug = request.args.get('show_slug')
    print(show_slug)
    try:
        myStorage = Storage(STORAGE_API_KEY, "shows-tnoradio", show_slug)
        theList = myStorage.GetStoragedObjectsList()
        return theList
    except Exception as e:
        print(e)
        return jsonify(e)
    
@app.route('/get_youtube_playlists', methods=['GET'])
def get_youtube_playlists():
    try:
        channel = request.args.get('channel', 'tnoradio')  # Default to 'tnoradio'
        myYoutube = Youtube(channel)
        playlists = myYoutube.get_playlists()
        return jsonify(playlists)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/get_video_stream', methods=['GET'])
def get_video_stream():
    try:
        guid = request.args.get('guid')
        resolution = request.args.get('resolution', '720p')
        format_type = request.args.get('format', 'mp4')
        
        if not guid:
            return jsonify({"error": "Missing required parameter: guid"}), 400
        
        video_library_id = os.environ.get("BUNNY_VIDEO_LIBRARY_ID", "286671")
        api_key = os.environ.get("BUNNY_API_KEY")
        
        if format_type == 'hls':
            # For HLS, we need to use the API to get the playlist URL
            if api_key:
                # Use BunnyCDN API to get the video info and generate proper URL
                import requests
                headers = {
                    'AccessKey': api_key,
                    'Content-Type': 'application/json'
                }
                
                # Get video info
                video_url = f"https://video.bunnycdn.com/library/{video_library_id}/videos/{guid}"
                response = requests.get(video_url, headers=headers)
                
                if response.status_code == 200:
                    video_data = response.json()
                    # Return the HLS playlist URL
                    hls_url = f"https://video.bunnycdn.com/stream/{video_library_id}/{guid}/playlist.m3u8"
                    return jsonify({"url": hls_url}), 200
                else:
                    return jsonify({"error": "Failed to get video info"}), 500
            else:
                # Fallback to direct URL (may not work for private videos)
                hls_url = f"https://video.bunnycdn.com/stream/{video_library_id}/{guid}/playlist.m3u8"
                return jsonify({"url": hls_url}), 200
        else:
            # For MP4, try to get the direct URL
            if api_key:
                # Use BunnyCDN API to get the video info
                import requests
                headers = {
                    'AccessKey': api_key,
                    'Content-Type': 'application/json'
                }
                
                # Get video info
                video_url = f"https://video.bunnycdn.com/library/{video_library_id}/videos/{guid}"
                response = requests.get(video_url, headers=headers)
                
                if response.status_code == 200:
                    video_data = response.json()
                    # Return the MP4 URL with specified resolution
                    mp4_url = f"https://video.bunnycdn.com/stream/{video_library_id}/{guid}/play_{resolution}.mp4"
                    return jsonify({"url": mp4_url}), 200
                else:
                    return jsonify({"error": "Failed to get video info"}), 500
            else:
                # Fallback to direct URL (may not work for private videos)
                mp4_url = f"https://video.bunnycdn.com/stream/{video_library_id}/{guid}/play_{resolution}.mp4"
                return jsonify({"url": mp4_url}), 200
            
    except Exception as e:
        logger.error(f"Error getting video stream: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_video_thumbnail', methods=['GET'])
def get_video_thumbnail():
    try:
        guid = request.args.get('guid')
        
        if not guid:
            return jsonify({"error": "Missing required parameter: guid"}), 400
        
        video_library_id = os.environ.get("BUNNY_VIDEO_LIBRARY_ID", "286671")
        api_key = os.environ.get("BUNNY_API_KEY")
        
        if api_key:
            # Use BunnyCDN API to get the video info and thumbnail
            import requests
            headers = {
                'AccessKey': api_key,
                'Content-Type': 'application/json'
            }
            
            # Get video info
            video_url = f"https://video.bunnycdn.com/library/{video_library_id}/videos/{guid}"
            response = requests.get(video_url, headers=headers)
            
            if response.status_code == 200:
                video_data = response.json()
                # Return the thumbnail URL
                thumbnail_url = f"https://video.bunnycdn.com/stream/{video_library_id}/{guid}/thumbnail.jpg"
                return jsonify({"url": thumbnail_url}), 200
            else:
                return jsonify({"error": "Failed to get video info"}), 500
        else:
            # Fallback to direct URL
            thumbnail_url = f"https://video.bunnycdn.com/stream/{video_library_id}/{guid}/thumbnail.jpg"
            return jsonify({"url": thumbnail_url}), 200
            
    except Exception as e:
        logger.error(f"Error getting video thumbnail: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_playlist_items', methods=['GET'])
def get_youtube_playlist_items():
    try:
        channel = request.args.get('channel', 'tnoradio')  # Default to 'tnoradio'
        playlist_name = request.args.get('playlist_name')
        if not playlist_name:
            return jsonify({"error": "playlist_name parameter is required"}), 400

        myYoutube = Youtube(channel)
        playlist_items = myYoutube.get_playlist_items(playlist_name)
        return playlist_items
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_all_episodes_sorted', methods=['GET'])
def get_all_episodes_sorted_route():
    try:
        # Get the playlist name from query parameters
        playlist_name = request.args.get('playlist_name')

        if not playlist_name:
            return jsonify({"error": "Missing playlist_name parameter"}), 400

        # Fetch the sorted episodes
        youtube = Youtube('tnoradio')  # Initialize Youtube class with default channel
        episodes = youtube.get_all_episodes_sorted(playlist_name)

        return jsonify(episodes), 200
    except Exception as e:
        print(f"Error fetching episodes: {e}")
        return jsonify({"error": "An error occurred while fetching episodes"}), 500

@app.route('/proxy_video/<guid>', methods=['GET'])
def proxy_video(guid):
    try:
        resolution = request.args.get('resolution', '720p')
        video_library_id = os.environ.get("BUNNY_VIDEO_LIBRARY_ID", "286671")
        api_key = os.environ.get("BUNNY_API_KEY")
        
        if not api_key:
            return jsonify({"error": "API key not configured"}), 500
        
        # Use BunnyCDN API to get the video info
        import requests
        headers = {
            'AccessKey': api_key,
            'Content-Type': 'application/json'
        }
        
        # Get video info
        video_url = f"https://video.bunnycdn.com/library/{video_library_id}/videos/{guid}"
        response = requests.get(video_url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to get video info"}), 500
        
        video_data = response.json()
        
        # Stream the video content through our server
        stream_url = f"https://video.bunnycdn.com/stream/{video_library_id}/{guid}/play_{resolution}.mp4"
        
        # Get the video stream with authentication
        stream_response = requests.get(stream_url, headers=headers, stream=True)
        
        if stream_response.status_code != 200:
            return jsonify({"error": "Failed to get video stream"}), 500
        
        # Return the video stream
        from flask import Response
        return Response(
            stream_response.iter_content(chunk_size=8192),
            content_type=stream_response.headers.get('content-type', 'video/mp4'),
            headers={
                'Content-Length': stream_response.headers.get('content-length'),
                'Accept-Ranges': 'bytes',
                'Cache-Control': 'public, max-age=3600'
            }
        )
        
    except Exception as e:
        logger.error(f"Error proxying video: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/proxy_thumbnail/<guid>', methods=['GET'])
def proxy_thumbnail(guid):
    try:
        video_library_id = os.environ.get("BUNNY_VIDEO_LIBRARY_ID", "286671")
        api_key = os.environ.get("BUNNY_API_KEY")
        
        if not api_key:
            return jsonify({"error": "API key not configured"}), 500
        
        # Use BunnyCDN API to get the video info
        import requests
        headers = {
            'AccessKey': api_key,
            'Content-Type': 'application/json'
        }
        
        # Get video info
        video_url = f"https://video.bunnycdn.com/library/{video_library_id}/videos/{guid}"
        response = requests.get(video_url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to get video info"}), 500
        
        video_data = response.json()
        
        # Get the thumbnail with authentication
        thumbnail_url = f"https://video.bunnycdn.com/stream/{video_library_id}/{guid}/thumbnail.jpg"
        thumbnail_response = requests.get(thumbnail_url, headers=headers)
        
        if thumbnail_response.status_code != 200:
            return jsonify({"error": "Failed to get thumbnail"}), 500
        
        # Return the thumbnail
        from flask import Response
        return Response(
            thumbnail_response.content,
            content_type=thumbnail_response.headers.get('content-type', 'image/jpeg'),
            headers={
                'Cache-Control': 'public, max-age=3600'
            }
        )
        
    except Exception as e:
        logger.error(f"Error proxying thumbnail: {e}")
        return jsonify({"error": str(e)}), 500

def handler(event, context):
    return {
        "statusCode": 200, 
        "body": json.dumps(event),
        "headers": {
                    "Content-Type": 'application/json',
                    "Access-Control-Allow-Origin": "*"
                },
        }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=19000, debug=True)
