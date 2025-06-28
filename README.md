# TNORadio CDN Service

Servicio CDN que actúa como proxy entre el frontend y Bunny.net, proporcionando endpoints REST para gestionar archivos, streams y contenido multimedia.

## 🚀 Nuevos Endpoints de Upload

### Upload de Archivos a Bunny.net

#### `POST /upload_file`
Sube un archivo directamente a Bunny.net Storage.

**Parámetros:**
- `show_slug` (form-data): Slug del show
- `image_type` (form-data): Tipo de imagen (ej: `ondemand_main`, `logo`, etc.)
- `file` (form-data): Archivo a subir

**Ejemplo:**
```bash
curl -X POST http://localhost:19000/upload_file \
  -F "show_slug=madressinfiltro" \
  -F "image_type=ondemand_main" \
  -F "file=@banner.png"
```

**Respuesta exitosa:**
```json
{
  "status": "success",
  "message": "File uploaded successfully to Bunny.net",
  "file_path": "ondemand_main/banner.png"
}
```

#### `DELETE /delete_file`
Elimina un archivo de Bunny.net Storage.

**Parámetros:**
- `show_slug` (query): Slug del show
- `image_type` (query): Tipo de imagen
- `filename` (query): Nombre del archivo

**Ejemplo:**
```bash
curl -X DELETE "http://localhost:19000/delete_file?show_slug=madressinfiltro&image_type=ondemand_main&filename=banner.png"
```

**Respuesta exitosa:**
```json
{
  "status": "success",
  "message": "File deleted successfully from Bunny.net"
}
```

#### `GET /list_files`
Lista archivos de un show específico en Bunny.net.

**Parámetros:**
- `show_slug` (query): Slug del show
- `image_type` (query, opcional): Tipo de imagen específico

**Ejemplo:**
```bash
curl "http://localhost:19000/list_files?show_slug=madressinfiltro&image_type=ondemand_main"
```

**Respuesta:**
```json
{
  "status": "success",
  "files": [
    {
      "File_Name": "banner.png"
    },
    {
      "File_Name": "logo.jpg"
    }
  ]
}
```

## 🔄 Flujo de Upload Completo

### Opción 1: Upload Directo (Recomendado)
```
Frontend → CDN Service → Bunny.net
```

### Opción 2: Upload con Image Service
```
Frontend → Image Service → FTP → CDN Service → Bunny.net
```

## 🛠️ Configuración

### Variables de Entorno
```bash
BUNNY_STORAGE_API_KEY=your_bunny_storage_api_key
```

### Estructura de Carpetas en Bunny.net
```
shows-tnoradio/
├── {show_slug}/
│   ├── logo/
│   ├── ondemand_main/
│   ├── ondemand_main_responsive/
│   ├── banner/
│   ├── responsive_banner/
│   ├── mini_banner/
│   └── minisite/
```

## 📋 Endpoints Existentes

### Stream Management
- `GET /get_stream` - Lista librerías de video
- `GET /get_videos` - Lista videos de una colección
- `GET /get_video_by_title` - Obtiene video por título
- `GET /get_stream_collections` - Lista colecciones

### File Management
- `GET /get_shows` - Lista archivos de un show
- `GET /list_files` - Lista archivos específicos
- `POST /upload_file` - Sube archivo a Bunny.net
- `DELETE /delete_file` - Elimina archivo de Bunny.net

### YouTube Integration
- `GET /get_youtube_playlists` - Lista playlists de YouTube
- `GET /get_playlist_items` - Obtiene items de playlist
- `GET /get_all_episodes_sorted` - Episodios ordenados

## 🔧 Desarrollo

### Instalación
```bash
pip install -r requirements.txt
```

### Ejecución
```bash
python app.py
```

### Puerto
El servicio corre en el puerto `19000`

## 🎯 Ventajas del Upload Directo

1. **Menor Latencia**: Sin intermediarios
2. **Mejor Performance**: Conexión directa a Bunny.net
3. **Menos Complejidad**: Un solo servicio involucrado
4. **Mejor Control**: Manejo directo de errores
5. **Escalabilidad**: Bunny.net maneja la carga

## 🔒 Seguridad

- Validación de tipos de archivo
- Límites de tamaño de archivo
- Autenticación por API key
- Sanitización de nombres de archivo
- Logs de auditoría

## 📊 Monitoreo

- Logs de upload/delete
- Métricas de performance
- Alertas de errores
- Health checks automáticos
