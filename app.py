from flask import Flask, request, jsonify, send_file, render_template_string
import os
import tempfile
import sys
import importlib.util
import shutil
from werkzeug.utils import secure_filename
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración temporal para guardar los videos descargados
TEMP_FOLDER = tempfile.mkdtemp()
app.config['TEMP_FOLDER'] = TEMP_FOLDER

# HTML template para la página principal
HOME_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>API de Descarga de Videos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        h2 {
            color: #444;
            margin-top: 30px;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: monospace;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>API de Descarga de Videos</h1>
    <p>Bienvenido a la API para descargar videos de YouTube, Instagram y TikTok.</p>
    
    <h2>Endpoints disponibles:</h2>
    <ul>
        <li><strong>POST /api/download</strong>: Descarga un video de la URL proporcionada</li>
        <li><strong>POST /api/info</strong>: Obtiene información del video sin descargarlo</li>
        <li><strong>POST /api/cleanup</strong>: Limpia archivos temporales del servidor</li>
    </ul>
    
    <h2>Ejemplo de uso:</h2>
    <p>Para descargar un video de YouTube:</p>
    <pre>
POST /api/download
Content-Type: application/json

{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "mp4"
}
    </pre>
    
    <h2>Plataformas soportadas:</h2>
    <ul>
        <li>YouTube</li>
        <li>Instagram</li>
        <li>TikTok</li>
    </ul>
</body>
</html>
"""

# Importar las funciones del script descargavideos.py
def import_descargavideos():
    try:
        # Intentar importar el módulo directamente
        import descargavideos
        logger.info("Módulo descargavideos importado directamente")
        return descargavideos
    except ImportError:
        logger.warning("No se pudo importar directamente, intentando importar desde archivo")
        try:
            # Intentar importar desde un archivo
            script_path = os.path.join(os.path.dirname(__file__), "descargavideos.py")
            if not os.path.exists(script_path):
                logger.error(f"El archivo {script_path} no existe")
                # Buscar el script en el directorio actual
                files = os.listdir('.')
                logger.info(f"Archivos en el directorio actual: {files}")
                raise FileNotFoundError(f"El archivo descargavideos.py no se encuentra en {script_path}")
                
            logger.info(f"Importando desde {script_path}")
            spec = importlib.util.spec_from_file_location("descargavideos", script_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["descargavideos"] = module
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Error al importar descargavideos.py: {e}")
            raise

# Página principal
@app.route('/', methods=['GET'])
def home():
    return render_template_string(HOME_PAGE_TEMPLATE)

# Endpoint principal para descargar videos
@app.route('/api/download', methods=['POST'])
def download_video():
    logger.info("Recibida solicitud en /api/download")
    
    if not request.is_json:
        logger.warning("La solicitud no es JSON")
        return jsonify({"error": "Se requiere un JSON con la URL"}), 400
    
    data = request.get_json()
    logger.info(f"Datos recibidos: {data}")
    
    if 'url' not in data:
        logger.warning("No se proporcionó URL")
        return jsonify({"error": "No se proporcionó una URL en el JSON"}), 400
    
    url = data['url']
    format_type = data.get('format', 'mp4')  # Por defecto formato mp4
    
    try:
        # Importar módulo de descarga
        descargavideos = import_descargavideos()
        
        # Crear directorio temporal para esta descarga
        download_dir = tempfile.mkdtemp(dir=app.config['TEMP_FOLDER'])
        logger.info(f"Directorio temporal creado: {download_dir}")
        
        # Determinar qué función usar según la URL
        if 'youtube.com' in url or 'youtu.be' in url:
            logger.info("Descargando video de YouTube")
            file_path = descargavideos.youtube_downloader(url, download_dir, format_type)
        elif 'instagram.com' in url:
            logger.info("Descargando video de Instagram")
            file_path = descargavideos.instagram_downloader(url, download_dir)
        elif 'tiktok.com' in url:
            logger.info("Descargando video de TikTok")
            file_path = descargavideos.tiktok_downloader(url, download_dir)
        else:
            logger.warning(f"URL no soportada: {url}")
            return jsonify({"error": "URL no soportada"}), 400
        
        logger.info(f"Archivo descargado en: {file_path}")
        
        if not file_path or not os.path.exists(file_path):
            logger.error("No se pudo descargar el video")
            return jsonify({"error": "No se pudo descargar el video"}), 500
        
        # Generar nombre de archivo seguro basado en la URL
        filename = secure_filename(os.path.basename(file_path))
        
        # Opciones de respuesta
        if data.get('return_file', True):  # Por defecto devolver el archivo
            logger.info(f"Enviando archivo: {filename}")
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename
            )
        else:
            # Solo devolver la URL o información sobre el archivo
            file_size = os.path.getsize(file_path)
            logger.info(f"Enviando información del archivo: {filename}, tamaño: {file_size}")
            return jsonify({
                "success": True,
                "file_name": filename,
                "file_size": file_size,
                "file_path": file_path
            })
            
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Endpoint para obtener información del video sin descargarlo
@app.route('/api/info', methods=['POST'])
def get_video_info():
    logger.info("Recibida solicitud en /api/info")
    
    if not request.is_json:
        return jsonify({"error": "Se requiere un JSON con la URL"}), 400
    
    data = request.get_json()
    if 'url' not in data:
        return jsonify({"error": "No se proporcionó una URL en el JSON"}), 400
    
    url = data['url']
    logger.info(f"Solicitando información para URL: {url}")
    
    try:
        # Importar módulo de descarga
        descargavideos = import_descargavideos()
        
        # Obtener información según la plataforma
        if 'youtube.com' in url or 'youtu.be' in url:
            logger.info("Obteniendo información de YouTube")
            info = descargavideos.get_youtube_info(url)
        elif 'instagram.com' in url:
            logger.info("Obteniendo información de Instagram")
            info = descargavideos.get_instagram_info(url)
        elif 'tiktok.com' in url:
            logger.info("Obteniendo información de TikTok")
            info = descargavideos.get_tiktok_info(url)
        else:
            logger.warning(f"URL no soportada: {url}")
            return jsonify({"error": "URL no soportada"}), 400
        
        logger.info(f"Información obtenida: {info}")
        return jsonify({
            "success": True,
            "info": info
        })
            
    except Exception as e:
        logger.error(f"Error al obtener información: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Limpiar archivos temporales periódicamente
@app.route('/api/cleanup', methods=['POST'])
def cleanup_temp_files():
    logger.info("Limpiando archivos temporales")
    try:
        for item in os.listdir(app.config['TEMP_FOLDER']):
            item_path = os.path.join(app.config['TEMP_FOLDER'], item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        logger.info("Archivos temporales eliminados correctamente")
        return jsonify({"success": True, "message": "Archivos temporales eliminados"})
    except Exception as e:
        logger.error(f"Error al limpiar archivos temporales: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Ruta para verificar la disponibilidad de la API
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "API funcionando correctamente"})

if __name__ == '__main__':
    # Asegurarse de que el directorio temporal exista
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
    
    # Obtener puerto de variables de entorno para compatibilidad con Render
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Iniciando aplicación en el puerto {port}")
    # Iniciar la aplicación
    app.run(host='0.0.0.0', port=port, debug=True)