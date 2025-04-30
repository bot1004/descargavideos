import requests
import json
import sys

# URL base del servicio (cambia según tu despliegue en Render.com)
BASE_URL = "https://descargavideos.onrender.com"

def test_api_status():
    """Comprueba si la API está activa y funcionando correctamente"""
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        
        print("✅ API funcionando correctamente")
        print("Información del servidor:")
        for key, value in response.json().items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar con la API: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Código de estado: {e.response.status_code}")
            print(f"Respuesta: {e.response.text}")
        return False

def test_download_youtube(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
    """Prueba la descarga de un video de YouTube"""
    try:
        payload = {
            "url": url,
            "format": "mp4",
            "return_file": False  # No descargar el archivo, solo obtener información
        }
        
        print(f"Probando descarga de YouTube: {url}")
        response = requests.post(f"{BASE_URL}/api/download", json=payload)
        response.raise_for_status()
        
        print("✅ Descarga de YouTube exitosa")
        print("Detalles del archivo:")
        for key, value in response.json().items():
            print(f"  {key}: {value}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al descargar video de YouTube: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Código de estado: {e.response.status_code}")
            print(f"Respuesta: {e.response.text}")
        return False

def test_info_youtube(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
    """Prueba la obtención de información de un video de YouTube"""
    try:
        payload = {
            "url": url
        }
        
        print(f"Probando información de YouTube: {url}")
        response = requests.post(f"{BASE_URL}/api/info", json=payload)
        response.raise_for_status()
        
        print("✅ Obtención de información de YouTube exitosa")
        print("Información del video:")
        info = response.json().get("info", {})
        for key, value in info.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")  # Truncar texto largo
            else:
                print(f"  {key}: {value}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener información de YouTube: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Código de estado: {e.response.status_code}")
            print(f"Respuesta: {e.response.text}")
        return False

def test_cleanup():
    """Prueba la limpieza de archivos temporales"""
    try:
        print("Probando limpieza de archivos temporales")
        response = requests.post(f"{BASE_URL}/api/cleanup")
        response.raise_for_status()
        
        print("✅ Limpieza de archivos temporales exitosa")
        print(f"Respuesta: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al limpiar archivos temporales: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Código de estado: {e.response.status_code}")
            print(f"Respuesta: {e.response.text}")
        return False

if __name__ == "__main__":
    print("===== PRUEBA DE API DE DESCARGA DE VIDEOS =====\n")
    
    # Verificar parámetros
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        print(f"Usando URL base: {BASE_URL}")
    
    # Ejecutar pruebas
    status_ok = test_api_status()
    
    if status_ok:
        print("\n===== PRUEBAS DE FUNCIONALIDAD =====\n")
        
        # YouTube
        if len(sys.argv) > 2 and sys.argv[2] == "youtube":
            url = sys.argv[3] if len(sys.argv) > 3 else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            test_info_youtube(url)
            test_download_youtube(url)
        # Instagram
        elif len(sys.argv) > 2 and sys.argv[2] == "instagram":
            url = sys.argv[3] if len(sys.argv) > 3 else None
            if url:
                # Implementar prueba de Instagram cuando se necesite
                print("Prueba de Instagram no implementada")
        # TikTok
        elif len(sys.argv) > 2 and sys.argv[2] == "tiktok":
            url = sys.argv[3] if len(sys.argv) > 3 else None
            if url:
                # Implementar prueba de TikTok cuando se necesite
                print("Prueba de TikTok no implementada")
        # Todos
        else:
            test_info_youtube()
            test_download_youtube()
            test_cleanup()