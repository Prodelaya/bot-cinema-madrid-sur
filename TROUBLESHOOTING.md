# 🔧 Troubleshooting - Bot de Cartelera Madrid Sur

Guía de resolución de problemas comunes durante desarrollo y despliegue.

---

## 📋 Índice

1. [Errores de Telegram Bot API](#-errores-de-telegram-bot-api)
2. [Problemas de Scraping](#-problemas-de-scraping)
3. [Errores de Despliegue en Railway](#-errores-de-despliegue-en-railway)
4. [Problemas con Docker](#-problemas-con-docker)
5. [Gestión de Git y permisos](#-gestión-de-git-y-permisos)

---

## 🤖 Errores de Telegram Bot API

### `Button_data_invalid`

**Error completo:**
```python
telegram.error.BadRequest: Button_data_invalid
```

**Causa:**
El `callback_data` de un `InlineKeyboardButton` supera los **64 bytes** permitidos por Telegram.

**Cómo identificarlo:**
```python
# ❌ Incorrecto - puede exceder límite
callback_data=f"pelicula_{titulo_muy_largo_con_version}"

# ✅ Correcto - usa índice
callback_data=f"peli_{idx}"  # Máximo "peli_999" = 8 bytes
```

**Solución:**
1. Crear lista de títulos en `context.user_data`
2. Usar índices numéricos en `callback_data`
3. Recuperar título mediante el índice al procesar callback

**Código de ejemplo:**
```python
# Al crear botones
titulos_lista = list(peliculas.keys())
context.user_data['titulos_lista'] = titulos_lista

keyboard = [
    [InlineKeyboardButton(titulo, callback_data=f"peli_{idx}")]
    for idx, titulo in enumerate(titulos_lista)
]

# Al recibir callback
idx = int(query.data.replace("peli_", ""))
titulo = context.user_data['titulos_lista'][idx]
```

**Referencias:**
- [Telegram Bot API - InlineKeyboardButton](https://core.telegram.org/bots/api#inlinekeyboardbutton)
- Commit que resuelve el problema: `fix: limite 64 bytes callback_data`

---

### `Conflict: terminated by other getUpdates request`

**Error completo:**
```python
telegram.error.Conflict: terminated by other getUpdates request
```

**Causa:**
Dos instancias del bot ejecutándose simultáneamente (por ejemplo: local + Railway).

**Solución:**
```bash
# Detener instancia local
# Linux/Mac
pkill -f bot.py

# Windows
taskkill /F /IM python.exe /FI "WINDOWTITLE eq bot.py"

# Verificar que solo Railway esté activo
curl https://api.telegram.org/bot<TOKEN>/getUpdates
```

**Prevención:**
- Usar variable de entorno `ENVIRONMENT=production` en Railway
- Añadir logging para identificar qué instancia está activa
- Configurar webhook en producción en lugar de polling (opcional)

---

### Bot no responde a comandos

**Síntomas:**
- El bot aparece online
- No hay errores en logs
- Los comandos no generan respuesta

**Checklist de diagnóstico:**
```bash
# 1. Verificar token
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TELEGRAM_BOT_TOKEN'))"

# 2. Probar comando directamente
curl https://api.telegram.org/bot<TOKEN>/getMe

# 3. Verificar updates pendientes
curl https://api.telegram.org/bot<TOKEN>/getUpdates

# 4. Revisar handlers en bot.py
grep "CommandHandler\|CallbackQueryHandler" bot.py
```

**Soluciones comunes:**
- Token incorrecto o expirado
- Handlers mal registrados en `main()`
- Otra instancia del bot consumiendo updates

---

## 🕷️ Problemas de Scraping

### FilmAffinity devuelve 403 Forbidden

**Error completo:**
```python
requests.exceptions.HTTPError: 403 Client Error: Forbidden
```

**Causa:**
FilmAffinity detecta scrapers por:
- User-Agent genérico (`python-requests/2.x`)
- Demasiadas requests desde una IP
- Ausencia de headers típicos de navegador

**Solución:**
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.filmaffinity.com/",
    "DNT": "1",
    "Connection": "keep-alive",
}

response = requests.get(URL, headers=HEADERS, timeout=10)
```

**Alternativas si persiste:**
- Usar proxy rotativo (ProxyMesh, ScraperAPI)
- Cambiar a fuente alternativa (eCartelera.com, SensaCine)
- Añadir delays entre requests: `time.sleep(random.uniform(1, 3))`
- Implementar retry logic con backoff exponencial

---

### Playwright: "Browser not found"

**Error completo:**
```
playwright._impl._api_types.Error: Executable doesn't exist at /home/...
```

**Causa:**
Chromium no está instalado tras instalar Playwright.

**Solución local:**
```bash
# Instalar Playwright
pip install playwright

# Instalar navegadores
playwright install chromium
```

**Solución Docker:**
Verificar que `Dockerfile` incluya:
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
```

**Nota:** Playwright requiere dependencias del sistema (ver sección Docker).

---

### Horarios vacíos o datos incompletos

**Síntomas:**
- `get_cinesa_showtimes()` devuelve lista vacía
- Películas sin horarios en `funciones`

**Diagnóstico:**
```python
# scrapers.py - añadir logging temporal
import logging
logging.basicConfig(level=logging.DEBUG)

def get_cinesa_showtimes():
    soup = BeautifulSoup(...)
    print(f"HTML length: {len(soup.text)}")  # Debe ser > 10000
    
    for titulo_tag in soup.select("span.fs-5"):
        print(f"Found: {titulo_tag.get_text()}")  # Debug
```

**Causas comunes:**
- Cambio en estructura HTML del sitio
- Selectores CSS desactualizados
- Timeout insuficiente en requests
- Web requiere JavaScript (migrar a Playwright)

**Solución:**
1. Inspeccionar HTML actual del sitio
2. Actualizar selectores CSS
3. Verificar que `data-sess-date` siga existiendo
4. Aumentar timeout: `requests.get(URL, timeout=30)`

---

## 🚀 Errores de Despliegue en Railway

### Bot no responde tras deploy (sin errores en logs)

**Síntomas:**
- Deploy exitoso
- Logs muestran "Bot ejecutándose..."
- Bot no responde a comandos en Telegram

**Diagnóstico:**
```bash
# 1. Verificar estado del servicio
# Railway Dashboard → Project → Settings → Status

# 2. Comprobar créditos disponibles
# Railway Dashboard → Account → Usage

# 3. Revisar plan activo
# Railway Dashboard → Settings → Plan
```

**Causa más común:**
El plan de prueba expiró o se agotó el crédito gratuito.

**Solución:**
1. Railway Dashboard → Settings → Plan
2. Click en **"Downgrade to Hobby Plan"**
3. Confirmar cambio
4. El bot se reactiva automáticamente en ~30 segundos

**Limitaciones del Hobby Plan:**
- **500 horas/mes** de ejecución (~20 días de uptime 24/7)
- **$5 USD** de crédito mensual
- Hibernación tras 30 minutos sin tráfico
- Se reactiva automáticamente con la primera request

---

### Docker build falla en Railway

**Error en logs:**
```
ERROR: failed to solve: process "/bin/sh -c apt-get update..." did not complete successfully
```

**Causa:**
- Timeout en instalación de dependencias
- Paquete del sistema no disponible
- Sintaxis incorrecta en `Dockerfile`

**Solución:**
```dockerfile
# Dockerfile optimizado
FROM python:3.11-slim

# Combinar comandos para reducir layers
RUN apt-get update && apt-get install -y \
    wget gnupg libglib2.0-0 libnss3 \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Chromium
RUN playwright install chromium --with-deps

COPY . .
CMD ["python", "bot.py"]
```

**Debugging:**
- Probar build localmente: `docker build -t test .`
- Revisar logs completos en Railway
- Verificar que `requirements.txt` no tenga errores

---

### Variables de entorno no se cargan

**Síntomas:**
```python
KeyError: 'TELEGRAM_BOT_TOKEN'
# o
TypeError: NoneType object is not callable
```

**Verificación:**
```python
# bot.py - añadir al inicio
import os
from dotenv import load_dotenv

load_dotenv()
print("BOT_TOKEN exists:", bool(os.getenv("TELEGRAM_BOT_TOKEN")))
print("TMDB_KEY exists:", bool(os.getenv("TMDB_API_KEY")))
```

**Solución Railway:**
1. Settings → Variables
2. Añadir variables faltantes:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABC...
   TMDB_API_KEY=abcd1234...
   ENVIRONMENT=production
   ```
3. Redeploy (Railway lo hace automáticamente)

**Nota:** Railway NO lee archivos `.env`, solo las variables del dashboard.

---

## 🐳 Problemas con Docker

### Dependencias de Playwright no resueltas

**Error:**
```
Error: Host system is missing dependencies to run browsers.
```

**Causa:**
Faltan librerías del sistema que Chromium necesita.

**Solución completa:**
```dockerfile
FROM python:3.11-slim

# Lista COMPLETA de dependencias Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY . .
CMD ["python", "bot.py"]
```

---

### Imagen Docker muy pesada

**Problema:**
Build tarda >10 minutos, imagen >1GB.

**Optimización:**
```dockerfile
# Usar imagen slim
FROM python:3.11-slim  # ~120MB vs ~900MB

# Limpiar caché apt
RUN apt-get update && apt-get install -y ... \
    && rm -rf /var/lib/apt/lists/*

# Desactivar cache pip
RUN pip install --no-cache-dir -r requirements.txt

# Multi-stage build (avanzado)
FROM python:3.11-slim AS builder
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libnss3 libgbm1 libxrandr2 \
    && rm -rf /var/lib/apt/lists/*
COPY . .
CMD ["python", "bot.py"]
```

**Comparativa de tamaños:**

| Configuración | Tamaño | Build time |
|---------------|--------|------------|
| python:3.11 (full) | ~1.2GB | 12-15 min |
| python:3.11-slim | ~650MB | 8-10 min |
| Multi-stage optimizado | ~450MB | 6-8 min |

**Comandos de diagnóstico:**
```bash
# Ver tamaño de imagen local
docker images cinema-bot

# Ver layers y sus tamaños
docker history cinema-bot

# Analizar qué ocupa espacio
docker run --rm cinema-bot du -sh /*
```

---

### Build falla por permisos en Railway

**Error:**
```
Error: permission denied while trying to connect to the Docker daemon socket
```

**Causa:**
Railway ejecuta builds en modo rootless por defecto desde 2024.

**Solución:**
Añadir al `Dockerfile`:
```dockerfile
# Asegurar permisos correctos
RUN chmod -R 755 /app

# Si usas archivos de datos
RUN mkdir -p /app/data && chmod 777 /app/data
```

**Alternativa:**
Configurar en `railway.toml`:
```toml
[build]
builder = "NIXPACKS"  # Cambiar de Docker a Nixpacks si persiste
```

---

### Container se reinicia constantemente

**Síntomas:**
```
Container exited with code 137
Container exited with code 143
```

**Diagnóstico:**
```bash
# Ver logs completos en Railway
railway logs

# Códigos de salida comunes:
# 137 = SIGKILL (memoria insuficiente)
# 143 = SIGTERM (terminación manual)
# 1 = Error de aplicación
```

**Soluciones según código:**

**137 (OOM - Out of Memory):**
```python
# bot.py - reducir uso de memoria
# Limitar caché de contexto
from telegram.ext import ContextTypes

async def cleanup_old_data(context: ContextTypes.DEFAULT_TYPE):
    # Limpiar datos antiguos cada hora
    if len(context.user_data) > 100:
        context.user_data.clear()
```

**143 (SIGTERM - Plan expirado):**
- Verificar créditos en Railway dashboard
- Downgrade a Hobby Plan si es necesario

**1 (Error de aplicación):**
```python
# Añadir try-catch global en bot.py
import logging
logging.basicConfig(level=logging.ERROR)

def main():
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        # ... handlers ...
        app.run_polling()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise
```

---

## 🔐 Gestión de Git y permisos

### `.env` subido accidentalmente al repositorio

**Síntomas:**
```
warning: .env appears in your repository history
```

**Impacto:**
- ⚠️ **Tokens expuestos públicamente** en GitHub
- ⚠️ **Posible compromiso de seguridad**
- ⚠️ **Violación de ToS de Telegram/TMDb**

**Solución inmediata:**

**1. Revocar credenciales comprometidas:**
```bash
# Telegram: hablar con @BotFather
/revoke

# TMDb: regenerar API key en:
# https://www.themoviedb.org/settings/api
```

**2. Eliminar `.env` del historial Git:**
```bash
# Usando git-filter-repo (recomendado)
pip install git-filter-repo
git filter-repo --invert-paths --path .env

# O usando BFG Repo-Cleaner
java -jar bfg.jar --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Forzar push (CUIDADO: reescribe historial)
git push origin --force --all
```

**3. Verificar que `.gitignore` funcione:**
```bash
# Comprobar que .env esté ignorado
git check-ignore -v .env
# Debería mostrar: .gitignore:XX:.env

# Si no está ignorado, añadirlo
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: asegurar .env en gitignore"
```

**Prevención:**
```bash
# Usar pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
if git diff --cached --name-only | grep -q "^.env$"; then
    echo "ERROR: Intentaste commitear .env"
    exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
```

---

### Error de permisos al clonar repositorio

**Error:**
```
Permission denied (publickey).
fatal: Could not read from remote repository.
```

**Causa:**
Clave SSH no configurada o no agregada a GitHub.

**Solución:**

**1. Verificar si tienes clave SSH:**
```bash
ls -al ~/.ssh
# Buscar id_rsa.pub o id_ed25519.pub
```

**2. Generar nueva clave si no existe:**
```bash
ssh-keygen -t ed25519 -C "tu_email@ejemplo.com"
# Presionar Enter para aceptar ubicación por defecto
# Presionar Enter para sin contraseña (o elegir una)
```

**3. Agregar clave al agente SSH:**
```bash
# Iniciar agente
eval "$(ssh-agent -s)"

# Agregar clave privada
ssh-add ~/.ssh/id_ed25519
```

**4. Copiar clave pública a GitHub:**
```bash
# Linux/Mac
cat ~/.ssh/id_ed25519.pub | pbcopy  # Mac
cat ~/.ssh/id_ed25519.pub | xclip   # Linux

# Windows (Git Bash)
cat ~/.ssh/id_ed25519.pub | clip

# Ir a GitHub → Settings → SSH Keys → New SSH key
# Pegar contenido y guardar
```

**5. Verificar conexión:**
```bash
ssh -T git@github.com
# Debería decir: "Hi usuario! You've successfully authenticated"
```

**Alternativa - usar HTTPS:**
```bash
# Cambiar remote de SSH a HTTPS
git remote set-url origin https://github.com/usuario/repo.git

# Configurar credential helper
git config --global credential.helper store
```

---

### `fatal: refusing to merge unrelated histories`

**Error al hacer pull:**
```
fatal: refusing to merge unrelated histories
```

**Causa:**
- Iniciaste repo local y remoto por separado
- No hay commit común entre ambos

**Solución:**
```bash
# Opción 1: Forzar merge (puede causar conflictos)
git pull origin main --allow-unrelated-histories

# Opción 2: Rebase desde cero (más limpio)
git fetch origin
git reset --hard origin/main

# Opción 3: Empezar de cero con el remoto
rm -rf .git
git clone https://github.com/usuario/repo.git
```

**Prevención:**
```bash
# Al crear repo nuevo, clonar primero
git clone https://github.com/usuario/repo.git
cd repo

# O inicializar con README en GitHub antes de clonar
```

---

### `.gitignore` no funciona para archivos ya trackeados

**Síntoma:**
```bash
git status
# Muestra __pycache__/ aunque está en .gitignore
```

**Causa:**
Git ya trackea los archivos antes de añadirlos al `.gitignore`.

**Solución:**
```bash
# Eliminar del índice (sin borrar archivos)
git rm -r --cached __pycache__/
git rm --cached .env

# Commitear cambios
git commit -m "chore: dejar de trackear archivos ignorados"

# Verificar
git status  # No debería mostrar archivos ignorados
```

**Limpieza completa:**
```bash
# Eliminar TODOS los archivos ignorados del índice
git rm -r --cached .
git add .
git commit -m "chore: aplicar .gitignore a todo el repo"
```

---

### Conflictos de merge al hacer pull

**Error:**
```
CONFLICT (content): Merge conflict in bot.py
Automatic merge failed; fix conflicts and then commit the result.
```

**Identificar conflictos:**
```bash
# Ver archivos en conflicto
git status

# Ver diferencias
git diff
```

**Resolver manualmente:**
```python
# bot.py contendrá marcadores:
<<<<<<< HEAD
# Tu código local
=======
# Código del remoto
>>>>>>> origin/main

# Editar archivo, eliminar marcadores y elegir versión correcta
# Guardar y marcar como resuelto:
git add bot.py
git commit -m "fix: resolver conflicto en bot.py"
```

**Resolución automática:**
```bash
# Aceptar siempre tu versión
git checkout --ours bot.py

# Aceptar siempre versión remota
git checkout --theirs bot.py

# Abortar merge y volver a estado previo
git merge --abort
```

**Prevención:**
```bash
# Pull frecuente antes de trabajar
git pull origin main

# Usar rebase en lugar de merge
git config --global pull.rebase true
```

---

## 🔍 Debugging avanzado

### Logs insuficientes en producción

**Problema:**
El bot falla en Railway pero no hay información útil en logs.

**Solución - añadir logging estructurado:**

```python
# bot.py - configurar logging detallado
import logging
import sys

# Configurar formato rico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Usar en handlers
async def handle_button_click(update, context):
    logger.info(f"Usuario {update.effective_user.id} clickeó: {query.data}")
    try:
        # ... lógica ...
    except Exception as e:
        logger.error(f"Error en button_click: {e}", exc_info=True)
```

**Nivel de logging según entorno:**
```python
# bot.py
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
```

**Railway variables:**
```
ENVIRONMENT=production
LOG_LEVEL=DEBUG  # Solo durante debugging
```

---

### Testing local de scrapers sin deploy

**Problema:**
Necesitas probar cambios en scrapers sin hacer push a Railway.

**Solución:**
```python
# scrapers.py - añadir al final
if __name__ == "__main__":
    import asyncio
    from pprint import pprint
    
    print("=== CINESA ===")
    pprint(get_cinesa_showtimes()[:2])
    
    print("\n=== YELMO ===")
    pprint(get_yelmo_showtimes()[:2])
    
    print("\n=== ODEON ===")
    pprint(asyncio.run(get_odeon_showtimes())[:2])
```

**Ejecutar tests:**
```bash
# Test rápido de scrapers
python scrapers.py

# Test con debug detallado
python -m pdb scrapers.py
```

**Mock de datos para development:**
```python
# mock_data.py
MOCK_CARTELERA = [
    {
        "titulo": "Película Test",
        "preventas": False,
        "funciones": [
            {
                "dia": "Viernes 22 de octubre",
                "horarios": [
                    {"hora": "16:00", "url": "https://example.com"}
                ]
            }
        ]
    }
]

# bot.py - usar en desarrollo
import os
if os.getenv("ENVIRONMENT") == "development":
    from mock_data import MOCK_CARTELERA
    cartelera = MOCK_CARTELERA
else:
    cartelera = get_cinesa_showtimes()
```

---

## 📚 Referencias útiles

### Documentación oficial
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot](https://docs.python-telegram-bot.org/)
- [Playwright Python](https://playwright.dev/python/docs/intro)
- [Railway Docs](https://docs.railway.app/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Herramientas de debugging
- [ngrok](https://ngrok.com/) - Túnel público para testing local de webhooks
- [RequestBin](https://requestbin.com/) - Inspector de requests HTTP
- [Dive](https://github.com/wagoodman/dive) - Analizar capas de imágenes Docker

### Comunidad
- [python-telegram-bot GitHub](https://github.com/python-telegram-bot/python-telegram-bot)
- [Railway Discord](https://discord.gg/railway)
- Stack Overflow: tags `python-telegram-bot`, `playwright`, `docker`

---

## ✅ Checklist de deployment

Antes de hacer deploy a producción, verificar:

- [ ] Variables de entorno configuradas en Railway
- [ ] `.env` en `.gitignore`
- [ ] Dockerfile con todas las dependencias
- [ ] Logging configurado con nivel INFO
- [ ] Timeouts aumentados para scrapers (>10s)
- [ ] Handlers probados localmente
- [ ] Token de Telegram válido
- [ ] API key de TMDb válida
- [ ] Railway plan activo (Hobby/Pro)
- [ ] Git history limpio (sin secrets)

**Test final antes de deploy:**
```bash
# Build local
docker build -t cinema-bot .

# Test completo
docker run --env-file .env cinema-bot

# Si funciona, push a GitHub
git push origin main
```

---

**Última actualización:** Octubre 2025  
**Contribuciones:** Issues y PRs bienvenidos en GitHub
