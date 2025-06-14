# 🎬 Bot de Cartelera – Cines Madrid Sur

---

## ✅ Estado del proyecto

💡 **Bot en activo**, desplegado en **Railway.app** (plan gratuito).\
🌐 Accesible 24/7 – puede *hibernar* si no recibe tráfico pero se reactiva automáticamente.\
🔗 **Pruébalo aquí →** [@cinema\_sur\_madrid\_bot](https://t.me/cinema_sur_madrid_bot)

---

## 🎓 Proyecto educativo autodidacta

> **⚠️ AVISO IMPORTANTE**\
> Este repositorio forma parte de un proyecto de **aprendizaje autodidacta** desarrollado por un estudiante de 1.º DAM/DAW con **asistencia 100 % de IA** (ChatGPT & Claude).\
> El objetivo principal es **dominar el ciclo completo** de desarrollo de software construyendo un producto real.

### 🤖 Rol de la IA en el proyecto

- **Mentoría:** sugerencias de arquitectura, elección de librerías, patrones de diseño.
- **Pair‑programming:** generación de bocetos de código que luego se analizaron y refactorizaron.
- **Debugging:** diagnóstico de errores de scraping, *timeouts* y conflictos de dependencias.


---

## 👨‍🎓 Sobre el autor

Proyecto realizado por **Pablo Laya**, estudiante de DAM/DAW en Madrid.\
Apasionado por **Python**, la automatización y los **bots de Telegram**.\
Este proyecto busca demostrar:

- Capacidad para **aprender de forma autodidacta** con ayuda de IA.
- Integrar scraping, APIs externas y DevOps en un producto funcional.
- Documentar el proceso para que otros estudiantes puedan replicarlo.

---

## 🚀 Características

| Funcionalidad              | Descripción                                                                     |
| -------------------------- | ------------------------------------------------------------------------------- |
| 🎬 **Cartelera en vivo**   | Horarios diarios de **Cinesa Parquesur**, **Odeón Sambil** y **Yelmo Islazul**. |
| 🖼️ **Info de películas**  | Sinopsis, póster, año y rating vía **TMDb API**.                                |
| 🧭 **Navegación sencilla** | Máx. 3 clics para llegar a la compra de entradas.                               |
| 🔄 **Scraping actual**     | Usa la fuente principal; *fallback* pendiente de implementar.                   |
| ⚙️ **Despliegue 24/7**     | Contenedor en Railway con webhook HTTPS.                                        |

---

## 🛠️ Tecnologías utilizadas

| Categoría            | Herramienta                                | Motivo                                    |
| -------------------- | ------------------------------------------ | ----------------------------------------- |
| Bot                  | `python-telegram-bot 20.7`                 | API madura con soporte `asyncio`.         |
| Scraping             | `requests`, `beautifulsoup4`, `playwright` | HTML estático y dinámico.                 |
| API externa          | **The Movie Database**                     | Metadatos y pósters en español.           |
| DevOps               | **Railway.app** + `gunicorn`               | Deploy continuo y webhook.                |
| Configuración        | `python-dotenv`                            | Variables de entorno seguras.             |
| Control de versiones | **Git & GitHub**                           | Seguimiento de cambios y *pull requests*. |

---

## 📁 Estructura del proyecto

```text
cinema-bot-madrid/
├── bot.py            # Núcleo del bot: comandos, callbacks, UX
├── scrapers.py       # Scrapers de los 3 cines + Playwright
├── tmdb_api.py       # Cliente ligero para The Movie Database
├── utils.py          # Helpers y caché (pendiente de refactor)
├── config.py         # Constantes y URLs
├── requirements.txt  # Dependencias
├── .env.example      # Plantilla de variables de entorno
├── Procfile          # Instrucción para Railway (gunicorn)
└── README.md         # Este documento
```

---

## 🖥️ Instalación y configuración

### 1 · Clona este repositorio

```bash
git clone https://github.com/tu-usuario/cinema-bot-madrid.git
cd cinema-bot-madrid
```

### 2 · Crea un entorno virtual (opcional pero recomendado)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate    # Windows
```

### 3 · Instala dependencias

```bash
pip install -r requirements.txt
```

### 4 · Configura las variables de entorno

1. Copia `.env.example` → `.env`.
2. Rellena:
   ```
   TELEGRAM_BOT_TOKEN=xxxxx
   TMDB_API_KEY=yyyyy
   ENVIRONMENT=development
   ```

### 5 · Ejecuta en local (long‑polling)

```bash
python bot.py
```

---

## 📡 ¿Cómo desplegar en Railway?

1. **New Project → Deploy from GitHub** y selecciona este repo.
2. Añade las mismas variables de entorno en el panel *Variables*.
3. Railway lee el **Procfile** y lanza `gunicorn bot:app`.
4. Crea el webhook:
   ```bash
   curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://<APP>.railway.app/"
   ```

¡Listo!

---

## 🖼️ Vista previa del bot

![Pantalla de inicio](/images/cine_inicio.png)

![Horarios con enlace](/images/horario_link.png)

![Información de la película](/images/info.png)

![Listado de películas](/images/pelis.png)


---

## 📝 Lecciones aprendidas

1. **Scraping dinámico:** para webs con JS hace falta un navegador headless.
2. **Fail‑fast:** múltiples fuentes mantienen el servicio online.
3. **DevOps temprano:** configurar CI/CD al principio evita sorpresas.
4. **IA ≠ magia:** leer y entender lo generado es el verdadero aprendizaje.

---

## 👤 Autor

**Pablo Laya** — estudiante de DAM/DAW, Madrid.\

---

## 📜 Licencia

Distribuido bajo la **MIT License**.

---

