"""
Cliente para The Movie Database (TMDb) API.
Obtiene información de películas: cartel, sinopsis, puntuación, etc.
"""

import requests
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Cargar variables de entorno
load_dotenv()

# Configuración de la API
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def buscar_pelicula(titulo: str) -> Optional[Dict[Any, Any]]:
    """
    Busca una película por título en TMDb.
    Retorna la primera coincidencia o None si no encuentra nada.
    """
    try:
        # Limpiar título para búsqueda (quitar versiones)
        titulo_limpio = titulo.split('(')[0].strip()
        
        url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": titulo_limpio,
            "language": "es-ES"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data["results"]:
            return data["results"][0]  # Primera coincidencia
        return None
        
    except Exception as e:
        print(f"Error buscando película '{titulo}': {e}")
        return None

def obtener_url_cartel(poster_path: str) -> str:
    """Convierte el poster_path en URL completa de imagen."""
    if poster_path:
        return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    return ""