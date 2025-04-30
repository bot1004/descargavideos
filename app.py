from flask import Flask, request, jsonify, send_file, render_template_string
import os
import tempfile
import sys
import importlib.util
import shutil
import platform
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración temporal para guardar los videos descargados
TEMP_FOLDER = tempfile.mkdtemp()
app.config['TEMP_FOLDER'] = TEMP_FOLDER

# HTML para la página principal
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Servicio de Descarga de Videos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        code {
            background-color: #f7f7f7;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: monospace;
        }
        pre {
            background-color: #f7f7f7;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .endpoint {
            background-color: #f7f7f7;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .method {
            font-weight: bold;
            color: #e74c3c;
        }
    </style>
</head>
<body>
    <h1>Servicio de Descarga de Videos</h1>
    <p>Esta API permite descargar videos de varias plataformas como YouTube, Instagram y TikTok.</p>
    
    <h2>Endpoints disponibles:</h2>
    
    <div class="endpoint">
        <p><span class="method">POST</span> /api/download</p>
        <p>Descarga un video desde la URL proporcionada.</p>
        <p><strong>Ejemplo de solicitud:</strong></p>
        <pre>
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "mp4",
    "return_file": true
}
        </pre>
    </div>
    
    <div class="endpoint">
        <p><span class="method">POST</span> /api/info</p>
        <p>Obtiene información sobre un video sin descargarlo.</p>
        <p><strong>Ejemplo de solicitud:</strong></p>
        <pre>
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
        </pre>
    </div>
    
    <div class="endpoint">
        <p><span class="method">POST</span> /api/cleanup</p>
        <p>Limpia los archivos temporales almacenados en el servidor.</p>
    </div>
    
    <h2>Estado del servidor:</h2>
    <p>El servidor está <strong>en línea</strong>.</p>
    <p>Versión de Python: {{ python_version }}</p>
    <p>Sistema operativo: {{ os_info }}</p>
    <p>Directorio temporal: {{ temp_dir }}</p>
</body>
</html>
"""

# Importar las funciones del script descargavideos.py
def import_descargavideos():
    script_path = os.path.join(os.path.dirname(__file__), "descargavideos.py")
    spec = importlib.util.spec_from_file_location("descargavideos", script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["descargavideos"] = module
    spec.loader.exec_module(module)
    return module

# Página principal - añadido para solucionar el error 404
@app.route('/')
def index():
    context = {
        'python_version': sys.version,
        'os_info': platform.system() + " " + platform.release(),
        'temp_dir': app.config['TEMP_FOLDER']
    }
    return render_template_string(INDEX_HTML, **context)

# Endpoint para verificar el estado de la API
@app.route('/api/status')
def status():
    try:
        # Verificar si podemos importar el módulo descargavideos
        descargavideos = import_descargavideos()
        module_status = "OK"
    except Exception as e:
        module_status = f"Error: {str(e)}"
    
    # Comprobar si el directorio temporal existe y tiene permisos de escritura
    temp_status = "OK"
    try:
        test_file = os.path.join(app.config['TEMP_FOLDER'], "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        temp_status = f"Error: {str(e)}"
    
    return jsonify({
        "status": "running",
        "python_version": sys.version,
        "os_info": platform.system() + " " + platform.release(),
        "descargavideos_module": module_status,
        "temp_directory": {
            "path": app.config['TEMP_FOLDER'],
            "status": temp_status
        }
    })

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