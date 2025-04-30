from flask import Flask, request, jsonify, send_file
import os
import tempfile
import sys
import importlib.util
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración temporal para guardar los videos descargados
TEMP_FOLDER = tempfile.mkdtemp()
app.config['TEMP_FOLDER'] = TEMP_FOLDER

# Importar las funciones del script descargavideos.py
def import_descargavideos():
    script_path = os.path.join(os.path.dirname(__file__), "descargavideos.py")
    spec = importlib.util.spec_from_file_location("descargavideos", script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["descargavideos"] = module
    spec.loader.exec_module(module)
    return module

# Endpoint principal para descargar videos
@app.route('/api/download', methods=['POST'])
def download_video():
    if not request.is_json:
        return jsonify({"error": "Se requiere un JSON con la URL"}), 400
    
    data = request.get_json()
    if 'url' not in data:
        return jsonify({"error": "No se proporcionó una URL en el JSON"}), 400
    
    url = data['url']
    format_type = data.get('format', 'mp4')  # Por defecto formato mp4
    
    try:
        # Importar módulo de descarga
        descargavideos = import_descargavideos()
        
        # Crear directorio temporal para esta descarga
        download_dir = tempfile.mkdtemp(dir=app.config['TEMP_FOLDER'])
        
        # Determinar qué función usar según la URL
        if 'youtube.com' in url or 'youtu.be' in url:
            file_path = descargavideos.youtube_downloader(url, download_dir, format_type)
        elif 'instagram.com' in url:
            file_path = descargavideos.instagram_downloader(url, download_dir)
        elif 'tiktok.com' in url:
            file_path = descargavideos.tiktok_downloader(url, download_dir)
        else:
            return jsonify({"error": "URL no soportada"}), 400
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "No se pudo descargar el video"}), 500
        
        # Generar nombre de archivo seguro basado en la URL
        filename = secure_filename(os.path.basename(file_path))
        
        # Opciones de respuesta
        if data.get('return_file', True):  # Por defecto devolver el archivo
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename
            )
        else:
            # Solo devolver la URL o información sobre el archivo
            file_size = os.path.getsize(file_path)
            return jsonify({
                "success": True,
                "file_name": filename,
                "file_size": file_size,
                "file_path": file_path
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para obtener información del video sin descargarlo
@app.route('/api/info', methods=['POST'])
def get_video_info():
    if not request.is_json:
        return jsonify({"error": "Se requiere un JSON con la URL"}), 400
    
    data = request.get_json()
    if 'url' not in data:
        return jsonify({"error": "No se proporcionó una URL en el JSON"}), 400
    
    url = data['url']
    
    try:
        # Importar módulo de descarga
        descargavideos = import_descargavideos()
        
        # Obtener información según la plataforma
        if 'youtube.com' in url or 'youtu.be' in url:
            info = descargavideos.get_youtube_info(url)
        elif 'instagram.com' in url:
            info = descargavideos.get_instagram_info(url)
        elif 'tiktok.com' in url:
            info = descargavideos.get_tiktok_info(url)
        else:
            return jsonify({"error": "URL no soportada"}), 400
        
        return jsonify({
            "success": True,
            "info": info
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Limpiar archivos temporales periódicamente (esto debería implementarse con un scheduler)
@app.route('/api/cleanup', methods=['POST'])
def cleanup_temp_files():
    try:
        for item in os.listdir(app.config['TEMP_FOLDER']):
            item_path = os.path.join(app.config['TEMP_FOLDER'], item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        return jsonify({"success": True, "message": "Archivos temporales eliminados"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Asegurarse de que el directorio temporal exista
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
    
    # Obtener puerto de variables de entorno para compatibilidad con Render
    port = int(os.environ.get('PORT', 5000))
    
    # Iniciar la aplicación
    app.run(host='0.0.0.0', port=port)