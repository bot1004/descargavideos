# Este es un ejemplo de las modificaciones que quizás necesites agregar
# al archivo descargavideos.py original para asegurar compatibilidad con la API

import os
import sys
import requests
from pytube import YouTube
import instaloader
from TikTokApi import TikTokApi

# Funciones para YouTube
def youtube_downloader(url, output_path=".", format="mp4"):
    """
    Descarga un video de YouTube
    
    Args:
        url: URL del video de YouTube
        output_path: Directorio donde se guardará el video
        format: Formato del video (mp4, mp3, etc.)
    
    Returns:
        La ruta al archivo descargado
    """
    try:
        yt = YouTube(url)
        
        if format.lower() == "mp3":
            # Descargar solo audio
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download(output_path)
            
            # Cambiar extensión a mp3
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            return new_file
        else:
            # Descargar video en la mejor calidad disponible
            video = yt.streams.get_highest_resolution()
            return video.download(output_path)
    except Exception as e:
        print(f"Error al descargar video de YouTube: {str(e)}")
        raise e

def get_youtube_info(url):
    """
    Obtiene información de un video de YouTube
    
    Args:
        url: URL del video de YouTube
    
    Returns:
        Diccionario con información del video
    """
    try:
        yt = YouTube(url)
        return {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "thumbnail_url": yt.thumbnail_url,
            "publish_date": str(yt.publish_date) if yt.publish_date else None
        }
    except Exception as e:
        print(f"Error al obtener información del video de YouTube: {str(e)}")
        raise e

# Funciones para Instagram
def instagram_downloader(url, output_path="."):
    """
    Descarga un video o imagen de Instagram
    
    Args:
        url: URL del post de Instagram
        output_path: Directorio donde se guardará el contenido
    
    Returns:
        La ruta al archivo descargado
    """
    try:
        # Extraer el shortcode del post
        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0]
        else:
            raise Exception("URL de Instagram inválida")
        
        # Configurar el descargador
        L = instaloader.Instaloader(dirname_pattern=output_path)
        
        # Descargar el post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Determinar la ruta del archivo
        file_path = os.path.join(output_path, f"{post.owner_username}_{post.shortcode}")
        
        # Descargar contenido
        if post.is_video:
            # Descargar video
            L.download_post(post, target=shortcode)
            return file_path + ".mp4"
        else:
            # Descargar imagen
            L.download_post(post, target=shortcode)
            return file_path + ".jpg"
    except Exception as e:
        print(f"Error al descargar contenido de Instagram: {str(e)}")
        raise e

def get_instagram_info(url):
    """
    Obtiene información de un post de Instagram
    
    Args:
        url: URL del post de Instagram
    
    Returns:
        Diccionario con información del post
    """
    try:
        # Extraer el shortcode del post
        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0]
        else:
            raise Exception("URL de Instagram inválida")
        
        # Configurar el descargador
        L = instaloader.Instaloader()
        
        # Obtener información del post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        return {
            "username": post.owner_username,
            "caption": post.caption if post.caption else "",
            "date": str(post.date),
            "likes": post.likes,
            "comments": post.comments,
            "is_video": post.is_video,
            "location": post.location.name if post.location else None
        }
    except Exception as e:
        print(f"Error al obtener información del post de Instagram: {str(e)}")
        raise e

# Funciones para TikTok
def tiktok_downloader(url, output_path="."):
    """
    Descarga un video de TikTok
    
    Args:
        url: URL del video de TikTok
        output_path: Directorio donde se guardará el video
    
    Returns:
        La ruta al archivo descargado
    """
    try:
        # Extraer el ID del video de TikTok
        if "/video/" in url:
            video_id = url.split("/video/")[1].split("?")[0]
        else:
            raise Exception("URL de TikTok inválida")
        
        # Usar API de TikTok
        with TikTokApi() as api:
            video = api.video(id=video_id)
            video_data = video.bytes()
            
            # Guardar el video
            output_file = os.path.join(output_path, f"{video_id}.mp4")
            with open(output_file, "wb") as f:
                f.write(video_data)
                
            return output_file
    except Exception as e:
        print(f"Error al descargar video de TikTok: {str(e)}")
        raise e

def get_tiktok_info(url):
    """
    Obtiene información de un video de TikTok
    
    Args:
        url: URL del video de TikTok
    
    Returns:
        Diccionario con información del video
    """
    try:
        # Extraer el ID del video de TikTok
        if "/video/" in url:
            video_id = url.split("/video/")[1].split("?")[0]
        else:
            raise Exception("URL de TikTok inválida")
        
        # Usar API de TikTok
        with TikTokApi() as api:
            video = api.video(id=video_id)
            
            return {
                "author": video.author.username,
                "description": video.description,
                "create_time": video.create_time,
                "duration": video.duration,
                "music": video.music.title,
                "likes": video.stats.likes,
                "comments": video.stats.comments,
                "shares": video.stats.shares,
                "views": video.stats.views
            }
    except Exception as e:
        print(f"Error al obtener información del video de TikTok: {str(e)}")
        raise e

# Punto de entrada para uso en línea de comandos
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python descargavideos.py [youtube|instagram|tiktok] [URL] [output_path] [format]")
        sys.exit(1)
        
    platform = sys.argv[1].lower()
    url = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "."
    format_type = sys.argv[4] if len(sys.argv) > 4 else "mp4"
    
    if platform == "youtube":
        file_path = youtube_downloader(url, output_path, format_type)
        print(f"Video descargado: {file_path}")
    elif platform == "instagram":
        file_path = instagram_downloader(url, output_path)
        print(f"Contenido descargado: {file_path}")
    elif platform == "tiktok":
        file_path = tiktok_downloader(url, output_path)
        print(f"Video descargado: {file_path}")
    else:
        print(f"Plataforma no soportada: {platform}")
        sys.exit(1)