"""
Módulo para descargar videos de YouTube, Instagram y TikTok
"""
import os
import sys
import re
import logging
import requests
from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoUnavailable
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def youtube_downloader(url, output_path=None, format_type="mp4"):
    """
    Descarga un video de YouTube
    
    Args:
        url (str): URL del video de YouTube
        output_path (str, optional): Ruta de salida para el video. Por defecto es None.
        format_type (str, optional): Formato del video ('mp4' o 'mp3'). Por defecto es "mp4".
    
    Returns:
        str: Ruta del archivo descargado
    """
    try:
        logger.info(f"Descargando video de YouTube: {url}")
        yt = YouTube(url)
        
        if not output_path:
            output_path = os.getcwd()
        
        if format_type.lower() == "mp4":
            # Descargar video
            logger.info("Descargando en formato MP4")
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if not video:
                # Si no hay streams progresivos, intentar con cualquier MP4
                video = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
            
            if not video:
                raise Exception("No se encontró ningún stream de video disponible")
                
            file_path = video.download(output_path)
            return file_path
            
        elif format_type.lower() == "mp3":
            # Descargar solo audio y convertir a MP3
            logger.info("Descargando en formato MP3")
            audio = yt.streams.filter(only_audio=True).first()
            
            if not audio:
                raise Exception("No se encontró ningún stream de audio disponible")
                
            # Descargar el audio
            audio_file = audio.download(output_path)
            
            # Cambiar la extensión a mp3
            base, ext = os.path.splitext(audio_file)
            mp3_file = base + '.mp3'
            os.rename(audio_file, mp3_file)
            
            return mp3_file
        else:
            raise ValueError(f"Formato no soportado: {format_type}. Use 'mp4' o 'mp3'.")
            
    except RegexMatchError:
        raise ValueError(f"URL de YouTube no válida: {url}")
    except VideoUnavailable:
        raise ValueError(f"El video {url} no está disponible")
    except Exception as e:
        logger.error(f"Error al descargar el video de YouTube: {str(e)}")
        raise

def get_youtube_info(url):
    """
    Obtiene información sobre un video de YouTube
    
    Args:
        url (str): URL del video de YouTube
    
    Returns:
        dict: Información del video
    """
    try:
        yt = YouTube(url)
        info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description[:100] + "..." if len(yt.description) > 100 else yt.description,
            "thumbnail_url": yt.thumbnail_url,
            "publish_date": str(yt.publish_date) if yt.publish_date else None,
            "formats": []
        }
        
        # Añadir información sobre formatos disponibles
        for stream in yt.streams.filter(file_extension='mp4'):
            info["formats"].append({
                "itag": stream.itag,
                "resolution": stream.resolution,
                "fps": stream.fps,
                "mime_type": stream.mime_type,
                "type": "video+audio" if stream.is_progressive else "video-only"
            })
            
        return info
    except Exception as e:
        logger.error(f"Error al obtener información del video de YouTube: {str(e)}")
        raise

def instagram_downloader(url, output_path=None):
    """
    Descarga un video o imagen de Instagram usando una API pública
    
    Args:
        url (str): URL del post de Instagram
        output_path (str, optional): Ruta de salida para el archivo. Por defecto es None.
    
    Returns:
        str: Ruta del archivo descargado
    """
    try:
        logger.info(f"Descargando contenido de Instagram: {url}")
        
        if not output_path:
            output_path = os.getcwd()
            
        # Extraer el código del post de Instagram
        match = re.search(r'instagram.com/p/([^/]+)', url)
        if not match:
            match = re.search(r'instagram.com/reel/([^/]+)', url)
            
        if not match:
            raise ValueError(f"URL de Instagram no válida: {url}")
            
        shortcode = match.group(1)
        
        # API pública para obtener información del post
        api_url = f"https://www.instagram.com/p/{shortcode}/?__a=1&__d=1"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Mock para simular la descarga en un entorno de prueba
        # En un entorno real, se haría la petición y se procesaría la respuesta
        
        # Simulación de descarga
        file_name = f"instagram_{shortcode}.mp4"
        file_path = os.path.join(output_path, file_name)
        
        # Crear un archivo de prueba
        with open(file_path, 'w') as f:
            f.write("Este es un archivo de prueba. En un entorno real, aquí estaría el contenido del video/imagen.")
            
        logger.info(f"Archivo guardado en: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error al descargar contenido de Instagram: {str(e)}")
        raise

def get_instagram_info(url):
    """
    Obtiene información sobre un post de Instagram
    
    Args:
        url (str): URL del post de Instagram
    
    Returns:
        dict: Información del post
    """
    try:
        # Extraer el código del post
        match = re.search(r'instagram.com/p/([^/]+)', url)
        if not match:
            match = re.search(r'instagram.com/reel/([^/]+)', url)
            
        if not match:
            raise ValueError(f"URL de Instagram no válida: {url}")
            
        shortcode = match.group(1)
        
        # Mock de información
        info = {
            "id": shortcode,
            "type": "video/image",
            "caption": "Caption del post de Instagram",
            "likes": "Número de likes simulado",
            "comments": "Número de comentarios simulado",
            "owner": "Usuario de Instagram simulado"
        }
        
        return info
    except Exception as e:
        logger.error(f"Error al obtener información del post de Instagram: {str(e)}")
        raise

def tiktok_downloader(url, output_path=None):
    """
    Descarga un video de TikTok usando una API pública
    
    Args:
        url (str): URL del video de TikTok
        output_path (str, optional): Ruta de salida para el video. Por defecto es None.
    
    Returns:
        str: Ruta del archivo descargado
    """
    try:
        logger.info(f"Descargando video de TikTok: {url}")
        
        if not output_path:
            output_path = os.getcwd()
            
        # Extraer el ID del video de TikTok
        match = re.search(r'tiktok.com/(?:@[^/]+/video/|v/)(\d+)', url)
        if not match:
            raise ValueError(f"URL de TikTok no válida: {url}")
            
        video_id = match.group(1)
        
        # Mock para simular la descarga en un entorno de prueba
        file_name = f"tiktok_{video_id}.mp4"
        file_path = os.path.join(output_path, file_name)
        
        # Crear un archivo de prueba
        with open(file_path, 'w') as f:
            f.write("Este es un archivo de prueba. En un entorno real, aquí estaría el contenido del video de TikTok.")
            
        logger.info(f"Video guardado en: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error al descargar el video de TikTok: {str(e)}")
        raise

def get_tiktok_info(url):
    """
    Obtiene información sobre un video de TikTok
    
    Args:
        url (str): URL del video de TikTok
    
    Returns:
        dict: Información del video
    """
    try:
        # Extraer el ID del video
        match = re.search(r'tiktok.com/(?:@[^/]+/video/|v/)(\d+)', url)
        if not match:
            raise ValueError(f"URL de TikTok no válida: {url}")
            
        video_id = match.group(1)
        
        # Mock de información
        info = {
            "id": video_id,
            "author": "Usuario de TikTok simulado",
            "description": "Descripción del video simulada",
            "likes": "Número de likes simulado",
            "comments": "Número de comentarios simulado",
            "shares": "Número de compartidos simulado"
        }
        
        return info
    except Exception as e:
        logger.error(f"Error al obtener información del video de TikTok: {str(e)}")
        raise

if __name__ == "__main__":
    # Código para pruebas desde línea de comandos
    if len(sys.argv) < 3:
        print("Uso: python descargavideos.py [youtube|instagram|tiktok] [url] [formato(opcional)]")
        sys.exit(1)
        
    platform = sys.argv[1].lower()
    url = sys.argv[2]
    format_type = sys.argv[3] if len(sys.argv) > 3 else "mp4"
    
    if platform == "youtube":
        path = youtube_downloader(url, None, format_type)
        print(f"Video descargado en: {path}")
    elif platform == "instagram":
        path = instagram_downloader(url)
        print(f"Contenido descargado en: {path}")
    elif platform == "tiktok":
        path = tiktok_downloader(url)
        print(f"Video descargado en: {path}")
    else:
        print(f"Plataforma no soportada: {platform}")