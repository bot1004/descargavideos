"""
Script para probar los endpoints de la API
"""
import requests
import json
import sys
import os

# URL de la API (cambia esto a tu URL de Render)
API_URL = "https://descargavideos.onrender.com"

def test_health():
    """Prueba el endpoint de health check"""
    url = f"{API_URL}/health"
    print(f"Probando endpoint de health check: {url}")
    
    try:
        response = requests.get(url)
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_info_endpoint(video_url):
    """Prueba el endpoint de información"""
    url = f"{API_URL}/api/info"
    print(f"Probando endpoint de info: {url}")
    
    data = {
        "url": video_url
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_download_endpoint(video_url, format_type="mp4"):
    """Prueba el endpoint de descarga"""
    url = f"{API_URL}/api/download"
    print(f"Probando endpoint de descarga: {url}")
    
    data = {
        "url": video_url,
        "format": format_type,
        "return_file": False  # Para que devuelva información en lugar del archivo
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Test de la API de Descarga de Videos ===")
    
    # Probar el endpoint de health
    print("\n1. Probando endpoint de health...")
    health_ok = test_health()
    
    if not health_ok:
        print("❌ El endpoint de health no está funcionando")
    else:
        print("✅ Endpoint de health funcionando correctamente")
    
    # Probar un video de YouTube
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"\n2. Probando endpoint de info con YouTube: {youtube_url}")
    info_ok = test_info_endpoint(youtube_url)
    
    if not info_ok:
        print("❌ El endpoint de info para YouTube no está funcionando")
    else:
        print("✅ Endpoint de info para YouTube funcionando correctamente")
    
    print(f"\n3. Probando endpoint de descarga con YouTube: {youtube_url}")
    download_ok = test_download_endpoint(youtube_url)
    
    if not download_ok:
        print("❌ El endpoint de descarga para YouTube no está funcionando")
    else:
        print("✅ Endpoint de descarga para YouTube funcionando correctamente")