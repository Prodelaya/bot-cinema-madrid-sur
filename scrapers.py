"""
Scrapers de carteleras para los cines del sur de Madrid.
Este archivo contiene funciones que extraen datos de sitios web públicos.
"""

import requests
import re
import subprocess
import os
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin

# URLs de los cines
URL_CINESA = "https://www.filmaffinity.com/es/theater-showtimes.php?id=264"
URL_YELMO = "https://www.filmaffinity.com/es/theater-showtimes.php?id=475"
URL_ODEON = "https://www.publicine.net/cartelera-cine/leganes/odeon-sambil"

# Configuración común
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Regex para limpiar fechas
RE_PREFIX = re.compile(
    r"^(hoy|mañana)\s*,?\s*",
    re.IGNORECASE
)

def dia_normalizado(fila: Tag) -> str:
    # ▸ día de la semana (con o sin prefijo)
    wday_raw = fila.select_one("span.wday").get_text(" ", strip=True)
    wday_clean = RE_PREFIX.sub("", wday_raw).strip()   # quita Hoy/Mañana/...

    # ▸ si hay mday cogemos el texto completo (número + mes)
    mday = fila.select_one("span.mday")
    if mday:
        fecha_completa = mday.get_text(strip=True)  # "11 de julio"
        return f"{wday_clean} {fecha_completa}"     # "Viernes 11 de julio"
    return wday_clean                               # "Viernes"

def get_cinesa_showtimes():
    soup = BeautifulSoup(requests.get(URL_CINESA, headers=HEADERS, timeout=10).text,
                         "html.parser")
    resultado = []

    for titulo_tag in soup.select("span.fs-5"):
        peli = {"titulo": titulo_tag.get_text(strip=True),
                "preventas": False,
                "funciones": []}

        nodo = titulo_tag.parent.find_next_sibling()
        while nodo and not nodo.find("span", class_="fs-5"):

            if nodo.find(class_="pre-sale-alert") or "Entradas en preventa" in nodo.get_text():
                peli["preventas"] = True

            # ▼ cada fila con data-sess-date es un día
            for fila in nodo.find_all(attrs={"data-sess-date": True}):
                dia_txt = dia_normalizado(fila)
                horarios = [
                    {"hora": a.get_text(strip=True), "url": a["href"]}
                    for a in fila.select("a.btn")
                ]
                if horarios:
                    peli["funciones"].append({"dia": dia_txt,
                                              "horarios": horarios})

            nodo = nodo.find_next_sibling()

        resultado.append(peli)

    return resultado

def get_yelmo_showtimes():
    soup = BeautifulSoup(requests.get(URL_YELMO, headers=HEADERS, timeout=10).text,
                         "html.parser")
    resultado = []

    for titulo_tag in soup.select("span.fs-5"):
        peli = {"titulo": titulo_tag.get_text(strip=True),
                "preventas": False,
                "funciones": []}

        nodo = titulo_tag.parent.find_next_sibling()
        while nodo and not nodo.find("span", class_="fs-5"):

            if nodo.find(class_="pre-sale-alert") or "Entradas en preventa" in nodo.get_text():
                peli["preventas"] = True

            # ▼ cada fila con data-sess-date es un día
            for fila in nodo.find_all(attrs={"data-sess-date": True}):
                dia_txt = dia_normalizado(fila)
                horarios = [
                    {"hora": a.get_text(strip=True), "url": a["href"]}
                    for a in fila.select("a.btn")
                ]
                if horarios:
                    peli["funciones"].append({"dia": dia_txt,
                                              "horarios": horarios})

            nodo = nodo.find_next_sibling()

        resultado.append(peli)

    return resultado


async def get_odeon_showtimes():
    """Scraper ASÍNCRONO para Odeón Sambil usando Playwright"""
    try:
        from playwright.async_api import async_playwright
        from urllib.parse import urljoin
        
        async with async_playwright() as p:
            # Lanzar Chromium
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Cargar la página y esperar que renderice
            print("Cargando página de Odeón...")
            await page.goto(URL_ODEON, timeout=30000)
            
            # Esperar a que aparezcan los elementos importantes
            await page.wait_for_selector("div.sessions", timeout=10000)
            
            # Esperar un poco más para asegurar que JS termine
            await page.wait_for_timeout(2000)
            
            # Obtener HTML ya renderizado
            html = await page.content()
            await browser.close()
            print("✅ HTML renderizado obtenido")
        
        # Procesar con BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        resultado = []
        
        for pelicula_session in soup.select("div.sessions"):
            # Extraer título
            titulo_h2 = pelicula_session.select_one("h2")
            if not titulo_h2:
                continue
            titulo = titulo_h2.get_text(strip=True)
            
            peli = {
                "titulo": titulo,
                "preventas": False,
                "funciones": []
            }
            
            # Buscar div.box
            box = pelicula_session.select_one("div.box")
            if not box:
                continue
            
            # Procesar días y horarios
            for dia_div in box.select("div.box_dia"):
                span_dia = dia_div.select_one("span.dia")
                if not span_dia:
                    continue
                    
                dia_texto = span_dia.get_text().replace('\n', ' ').strip()
                
                # Buscar el siguiente box_projeccions hermano
                projeccions = dia_div.find_next_sibling("div", class_="box_projeccions")
                if not projeccions:
                    continue
                
                horarios = []
                for link in projeccions.select("a[data-href]"):
                    hora_div = link.select_one("div.horari_pelicula")
                    if hora_div:
                        hora_texto = hora_div.get_text().strip().split('\n')[0]
                        # Limpiar sufijos como ATMOS, DIGITAL, DOLBY, etc.
                        hora_texto = re.sub(r'(ATMOS|DIGITAL|DOLBY|VIP|3D|4D)$', '', hora_texto).strip()
                        url = urljoin(URL_ODEON, link.get("data-href", ""))
                        horarios.append({"hora": hora_texto, "url": url})
                
                if horarios:
                    peli["funciones"].append({
                        "dia": dia_texto,
                        "horarios": horarios
                    })
            
            if peli["funciones"]:
                resultado.append(peli)
        
        print(f"✅ {len(resultado)} películas encontradas en Odeón")
        return resultado
        
    except ImportError:
        print("❌ Playwright no está instalado")
        return []
    except Exception as e:
        print(f"❌ Error con Playwright: {e}")
        return []
    
# ── test rápido ──────────────────────────────────────────────────────
if __name__ == "__main__":
    from pprint import pprint
    print("=== CINESA ===")
    pprint(get_cinesa_showtimes()[:2], sort_dicts=False)
    print("\n=== YELMO ===")
    pprint(get_yelmo_showtimes()[:2], sort_dicts=False)
    print("\n=== ODEON ===")
    pprint(get_odeon_showtimes()[:2], sort_dicts=False)
    