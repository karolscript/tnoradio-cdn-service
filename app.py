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
