# 🎬 Bot de Cartelera – Cines Madrid Sur

---

## ✅ Estado del proyecto

💡 **Bot en activo**, desplegado en **Railway.app** (plan gratuito).\
🌐 Accesible 24/7 – puede *hibernar* si no recibe tráfico pero se reactiva automáticamente.\
🔗 **Pruébalo aquí →** [@cinema\_sur\_madrid\_bot](https://t.me/cinema_sur_madrid_bot)

---

## 🎓 Proyecto educativo autodidacta

> **⚠️ AVISO IMPORTANTE**\
> Este repositorio forma parte de un proyecto de **aprendizaje autodidacta** desarrollado por un estudiante de 1.º DAM/DAW con **asistencia 100 % de IA** (ChatGPT & Claude).\
> El objetivo principal es **dominar el ciclo completo** de desarrollo de software construyendo un producto real, incluyendo **containerización** y **DevOps**.

### 🤖 Rol de la IA en el proyecto

- **Mentoría:** sugerencias de arquitectura, elección de librerías, patrones de diseño.
- **Pair‑programming:** generación de bocetos de código que luego se analizaron y refactorizaron.
- **Debugging:** diagnóstico de errores de scraping, *timeouts* y conflictos de dependencias.
- **DevOps:** resolución de problemas de despliegue, containerización con Docker y configuración de entornos de producción.


---

## 👨‍🎓 Sobre el autor

Proyecto realizado por **Pablo Laya**, estudiante de DAM/DAW en Madrid.\
Apasionado por **Python**, la automatización y los **bots de Telegram**.\
Este proyecto busca demostrar:

- Capacidad para **aprender de forma autodidacta** con ayuda de IA.
- Integrar scraping, APIs externas, containerización y DevOps en un producto funcional.
- Resolver problemas reales de **dependencias del sistema** y **web scraping dinámico**.
- Documentar el proceso para que otros estudiantes puedan replicarlo.

---

## 🚀 Características

| Funcionalidad              | Descripción                                                                     |
| -------------------------- | ------------------------------------------------------------------------------- |
| 🎬 **Cartelera en vivo**   | Horarios diarios de **Cinesa Parquesur**, **Odeón Sambil** y **Yelmo Islazul**. |
| 🖼️ **Info de películas**  | Sinopsis, póster, año y rating vía **TMDb API**.                                |
| 🧭 **Navegación sencilla** | Máx. 3 clics para llegar a la compra de entradas.                               |
| 🔄 **Scraping avanzado**   | HTML estático (BeautifulSoup) + dinámico (Playwright + Chromium).               |
| ⚙️ **Despliegue 24/7**     | Contenedor Docker en Railway con todas las dependencias incluidas.              |
| 🐳 **Containerización**    | Dockerfile optimizado para resolver dependencias del sistema.                   |

---

## 🛠️ Tecnologías utilizadas

| Categoría               | Herramienta                                | Motivo                                           |
| ----------------------- | ------------------------------------------ | ------------------------------------------------ |
| Bot                     | `python-telegram-bot 20.7`                 | API madura con soporte `asyncio`.               |
| Scraping estático       | `requests`, `beautifulsoup4`               | Cinesa y Yelmo (HTML directo de FilmAffinity).   |
| Scraping dinámico       | `playwright + chromium`                    | Odeón Sambil (requiere renderizado JavaScript).  |
| API externa             | **The Movie Database**                     | Metadatos y pósters en español.                 |
| Containerización        | **Docker**                                 | Resolver dependencias del sistema para Playwright. |
| DevOps                  | **Railway.app**                            | Deploy continuo con Docker support.             |
| Configuración           | `python-dotenv`                            | Variables de entorno seguras.                   |
| Control de versiones    | **Git & GitHub**                           | Seguimiento de cambios y deploy automático.     |

---

## 🐳 ¿Por qué Docker?

### **Problema inicial:**
El scraping de **Odeón Sambil** requiere **Playwright + Chromium**, que necesita múltiples dependencias del sistema:
```bash
libglib2.0-0, libnss3, libgbm1, libxrandr2, libpango-1.0-0...
```

### **Desafío en Railway:**
- ❌ **Sin Docker**: usuarios sin privilegios → `apt-get install` falla
- ❌ **Procfile + buildpacks**: dependencias inconsistentes
- ❌ **Scripts de instalación**: permisos limitados

### **Solución con Docker:**
- ✅ **Build con root**: `RUN apt-get install` funciona perfecto
- ✅ **Imagen completa**: todas las dependencias incluidas
- ✅ **Reproducible**: mismo entorno en desarrollo y producción
- ✅ **Aislamiento**: no afecta al sistema host

---

## 📁 Estructura del proyecto

```text
cinema-bot-madrid/
├── Dockerfile        # Imagen optimizada con Playwright + dependencias
├── bot.py            # Núcleo del bot: comandos, callbacks, UX
├── scrapers.py       # Scrapers de los 3 cines (BeautifulSoup + Playwright)
├── tmdb_api.py       # Cliente ligero para The Movie Database
├── requirements.txt  # Dependencias Python
├── .env.example      # Plantilla de variables de entorno
└── README.md         # Este documento
```

---

## 🧩 Arquitectura de scraping

### **Estrategia híbrida implementada:**

#### **Cinesa Parquesur & Yelmo Islazul** → Scraping estático
```python
# Fuente: FilmAffinity (HTML directo)
soup = BeautifulSoup(requests.get(URL).text, "html.parser")
```
- ✅ **Rápido y eficiente**
- ✅ **Pocos recursos**
- ✅ **Datos estructurados**

#### **Odeón Sambil** → Scraping dinámico
```python
# Fuente: Web oficial (JavaScript + DOM dinámico)
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(URL)
    html = await page.content()
```
- ✅ **Datos más actualizados**
- ✅ **Renderiza JavaScript**
- ⚠️ **Requiere Chromium** (solucionado con Docker)

### **Normalización de datos:**
- **Horarios limpios**: `"16:00ATMOS"` → `"16:00"`
- **Fechas normalizadas**: `"Hoy, viernes"` → `"Viernes 15 de junio"`
- **URLs absolutas**: Links relativos convertidos a URLs completas

---

## 🖥️ Instalación y configuración

### 1 · Clona este repositorio

```bash
git clone https://github.com/pablolaya-dev/bot-cinema-madrid-sur.git
cd bot-cinema-madrid-sur
```

### 2 · Opción A: Desarrollo local con Docker (recomendado)

```bash
# Construir imagen
docker build -t cinema-bot .

# Ejecutar contenedor
docker run --env-file .env cinema-bot
```

### 3 · Opción B: Desarrollo local sin Docker

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar Playwright + Chromium
playwright install chromium
```

### 4 · Configura las variables de entorno

1. Copia `.env.example` → `.env`.
2. Rellena:
   ```
   TELEGRAM_BOT_TOKEN=xxxxx
   TMDB_API_KEY=yyyyy
   ENVIRONMENT=development
   ```

### 5 · Ejecuta en local

```bash
python bot.py
```

---

## 📡 ¿Cómo desplegar en Railway?

### **Despliegue con Docker (método actual):**

1. **New Project → Deploy from GitHub** y selecciona este repo.
2. Railway **auto-detecta** el `Dockerfile` y usa Docker build.
3. Añade las variables de entorno en el panel *Variables*:
   ```
   TELEGRAM_BOT_TOKEN=xxxxx
   ENVIRONMENT=production
   ```
4. **Deploy automático** → Railway construye la imagen con todas las dependencias.

### **¿Por qué Railway + Docker?**
- ✅ **Tier gratuito** generoso (500 horas/mes)
- ✅ **Auto-deploy** desde GitHub commits
- ✅ **Docker support** nativo
- ✅ **Logs en tiempo real** para debugging
- ✅ **Variables de entorno** seguras

---

## 🖼️ Vista previa del bot

![Pantalla de inicio](/images/cine_inicio.png)

![Horarios con enlace](/images/horario_link.png)

![Información de la película](/images/info.png)

![Listado de películas](/images/pelis.png)


---

## 🔄 Evolución del proyecto

### **Cronología del desarrollo:**

#### **Fase 1: MVP básico** (Días 1-3)
- ✅ Bot funcional con 2 cines (Cinesa + Yelmo)
- ✅ Scraping con BeautifulSoup
- ✅ Integración TMDb API
- ✅ Navegación con botones inline

#### **Fase 2: Desafío técnico** (Días 4-5)
- 🎯 **Objetivo**: Añadir Odeón Sambil
- 🚧 **Problema**: Web usa JavaScript → BeautifulSoup no funciona
- ✅ **Solución**: Migrar a Playwright + Chromium

#### **Fase 3: Problemas de despliegue** (Días 6-7)
- 🚧 **Problema**: Playwright requiere dependencias del sistema
- ❌ **Intento 1**: Railway con Procfile → Permisos insuficientes
- ❌ **Intento 2**: Render.com → Limitaciones tier gratuito
- ❌ **Intento 3**: Heroku → Workers de pago ($7/mes)
- ✅ **Solución final**: Railway + Docker → ¡Funciona!

### **Lecciones aprendidas de DevOps:**
1. **Dependencias del sistema** ≠ dependencias de Python
2. **Docker resuelve** problemas de permisos y reproducibilidad
3. **Platform-as-a-Service** tiene limitaciones → containers dan más control
4. **Free tiers** varían mucho entre proveedores

---

## 📝 Lecciones aprendidas

### **Técnicas:**
1. **Scraping dinámico:** para webs con JS hace falta un navegador headless.
2. **Arquitectura híbrida:** combinar técnicas según la fuente de datos.
3. **Fail‑fast:** múltiples fuentes mantienen el servicio online.
4. **Containerización:** Docker resuelve problemas de dependencias complejas.

### **DevOps:**
1. **Deploy temprano:** configurar CI/CD al principio evita sorpresas.
2. **Platform limitations:** cada PaaS tiene restricciones específicas.
3. **Container strategy:** cuando buildpacks fallan, Docker siempre funciona.
4. **Environment parity:** desarrollo y producción deben ser idénticos.

### **Colaboración con IA:**
1. **IA ≠ magia:** leer y entender lo generado es el verdadero aprendizaje.
2. **Debugging iterativo:** IA ayuda a diagnosticar, pero hay que entender la causa.
3. **Architecture decisions:** IA sugiere, pero la decisión final es del desarrollador.

---

## 👤 Autor

**Pablo Laya** — estudiante de DAM/DAW, Madrid.
**GitHub**: [pablolaya-dev](https://github.com/pablolaya-dev)

---

## 📜 Licencia

Distribuido bajo la **MIT License**.

---

