# bot.py
"""
Bot de Telegram para consultar la cartelera de cines del sur de Madrid.
Desarrollado como proyecto educativo asistido por IA.
"""

# 📦 Importaciones necesarias
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from scrapers import get_cinesa_showtimes, get_odeon_showtimes, get_yelmo_showtimes
from tmdb_api import buscar_pelicula, obtener_url_cartel  # ← NUEVA LÍNEA

# 🔐 Cargar las variables de entorno desde el archivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 🎬 Comando /start: muestra los botones con los cines
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Crear botones inline con los nombres de los cines
    keyboard = [
        [
            InlineKeyboardButton("🎟️ Cinesa Parquesur", callback_data="cinesa"),
            InlineKeyboardButton("🎥 Odeón Sambil", callback_data="odeon"),
            InlineKeyboardButton("🍿 Yelmo Islazul", callback_data="yelmo"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Enviar el mensaje con los botones
    await update.message.reply_text(
        "🎬 ¡Bienvenido al Bot de Cartelera de Madrid Sur!\n\n"
        "Selecciona un cine para ver la cartelera:",
        reply_markup=reply_markup
    )

# 🎯 Función que maneja los clics en los botones inline
async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Confirma que el clic se ha recibido

    cine_seleccionado = query.data  # callback_data: "cinesa", "odeon", "yelmo"

    # Respuesta diferente según el botón pulsado
    if cine_seleccionado == "cinesa":
        # Obtener cartelera
        cartelera = get_cinesa_showtimes()
        
        # Guardar en contexto para uso posterior
        context.user_data['cartelera_actual'] = cartelera
        context.user_data['cine_actual'] = 'cinesa'
        
        # Agrupar películas por título base (sin versiones)
        peliculas_agrupadas = {}
        for pelicula in cartelera:
            titulo = pelicula['titulo']
            # Extraer título base (antes del primer paréntesis)
            titulo_base = titulo.split('(')[0].strip()
            
            if titulo_base not in peliculas_agrupadas:
                peliculas_agrupadas[titulo_base] = []
            peliculas_agrupadas[titulo_base].append(pelicula)
        
        context.user_data['peliculas_agrupadas'] = peliculas_agrupadas
    
        # Crear botones con títulos base únicos
        keyboard = []
        for titulo_base in peliculas_agrupadas:
            # Verificar si alguna versión tiene preventas
            tiene_preventas = any(pelicula['preventas'] for pelicula in peliculas_agrupadas[titulo_base])
            
            # Añadir indicador de preventa si es necesario
            texto_boton = f"🎬 {titulo_base}"
            if tiene_preventas:
                texto_boton += " (Preventa)"
            
            keyboard.append([InlineKeyboardButton(texto_boton, callback_data=f"pelicula_{texto_boton.replace('🎬 ', '')}")])

        # Añadir botón volver
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_cines")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🎟️ *Cinesa Parquesur* - Películas disponibles:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return  # Importante: salir aquí para no ejecutar el edit_message_text del final
    
    elif cine_seleccionado == "odeon":
        # Obtener cartelera
        cartelera = await get_odeon_showtimes()
        
        # Guardar en contexto para uso posterior
        context.user_data['cartelera_actual'] = cartelera
        context.user_data['cine_actual'] = 'odeon'
        
        # Agrupar películas por título base (sin versiones)
        peliculas_agrupadas = {}
        for pelicula in cartelera:
            titulo = pelicula['titulo']
            # Extraer título base (antes del primer paréntesis)
            titulo_base = titulo.split('(')[0].strip()
            
            if titulo_base not in peliculas_agrupadas:
                peliculas_agrupadas[titulo_base] = []
            peliculas_agrupadas[titulo_base].append(pelicula)
        
        context.user_data['peliculas_agrupadas'] = peliculas_agrupadas

        # Crear botones con títulos base únicos
        keyboard = []
        for titulo_base in peliculas_agrupadas:
            # Verificar si alguna versión tiene preventas
            tiene_preventas = any(pelicula['preventas'] for pelicula in peliculas_agrupadas[titulo_base])
            
            # Añadir indicador de preventa si es necesario
            texto_boton = f"🎬 {titulo_base}"
            if tiene_preventas:
                texto_boton += " (Preventa)"
            
            keyboard.append([InlineKeyboardButton(texto_boton, callback_data=f"pelicula_{texto_boton.replace('🎬 ', '')}")])

        # Añadir botón volver
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_cines")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🎥 *Odeón Sambil* - Películas disponibles:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return  # Importante: salir aquí para no ejecutar el edit_message_text del final

    elif cine_seleccionado == "yelmo":
        # Obtener cartelera (igual que Cinesa)
        cartelera = get_yelmo_showtimes()
        
        # Guardar en contexto para uso posterior
        context.user_data['cartelera_actual'] = cartelera
        context.user_data['cine_actual'] = 'yelmo'
        
        # Agrupar películas por título base (sin versiones)
        peliculas_agrupadas = {}
        for pelicula in cartelera:
            titulo = pelicula['titulo']
            # Extraer título base (antes del primer paréntesis)
            titulo_base = titulo.split('(')[0].strip()
            
            if titulo_base not in peliculas_agrupadas:
                peliculas_agrupadas[titulo_base] = []
            peliculas_agrupadas[titulo_base].append(pelicula)
        
        context.user_data['peliculas_agrupadas'] = peliculas_agrupadas

        # Crear botones con títulos base únicos
        keyboard = []
        for titulo_base in peliculas_agrupadas:
            # Verificar si alguna versión tiene preventas
            tiene_preventas = any(pelicula['preventas'] for pelicula in peliculas_agrupadas[titulo_base])
            
            # Añadir indicador de preventa si es necesario
            texto_boton = f"🎬 {titulo_base}"
            if tiene_preventas:
                texto_boton += " (Preventa)"
            
            keyboard.append([InlineKeyboardButton(texto_boton, callback_data=f"pelicula_{texto_boton.replace('🎬 ', '')}")])

        # Añadir botón volver
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_cines")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🍿 *Yelmo Islazul* - Películas disponibles:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return
    else:
        mensaje = "❓ Cine no reconocido."

    # Enviar respuesta
    await query.edit_message_text(text=mensaje, parse_mode="Markdown")

# 🎬 Función que maneja la selección de una película
async def handle_movie_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Extraer título base del callback_data
    titulo_base_raw = query.data.replace("pelicula_", "")
    titulo_base = titulo_base_raw.replace(" (Preventa)", "").strip()

    
    # Obtener versiones de esta película
    peliculas_agrupadas = context.user_data.get('peliculas_agrupadas', {})
    versiones = peliculas_agrupadas.get(titulo_base, [])
    
    if len(versiones) == 1:
        # Solo una versión → ir directamente a opciones (horarios/info)
        pelicula = versiones[0]
        context.user_data['pelicula_seleccionada'] = pelicula
        
        keyboard = [
            [InlineKeyboardButton("📅 Ver horarios", callback_data="ver_horarios")],
            [InlineKeyboardButton("📖 Ver información", callback_data="ver_info")],
            [InlineKeyboardButton("🔙 Volver", callback_data="volver_peliculas")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"🎬 *{pelicula['titulo']}*\n\n¿Qué quieres hacer?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        # Múltiples versiones → mostrar botones de versión
        context.user_data['versiones_actuales'] = versiones

        keyboard = []
        for i, pelicula in enumerate(versiones):
            titulo_completo = pelicula['titulo']
            keyboard.append([InlineKeyboardButton(f"🎭 {titulo_completo}", callback_data=f"version_{i}")])

        # Añadir botón volver
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_peliculas")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"🎬 *{titulo_base}*\n\nSelecciona la versión:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# 📅 Función que maneja la selección de una versión específica        
async def handle_version_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Extraer índice de la versión del callback_data
    version_index = int(query.data.replace("version_", ""))
    
    # Obtener la versión específica
    versiones_actuales = context.user_data.get('versiones_actuales', [])
    pelicula = versiones_actuales[version_index]
    
    # Guardar la película seleccionada
    context.user_data['pelicula_seleccionada'] = pelicula
    
    # Mostrar opciones (horarios/info)
    keyboard = [
        [InlineKeyboardButton("📅 Ver horarios", callback_data="ver_horarios")],
        [InlineKeyboardButton("📖 Ver información", callback_data="ver_info")],
        [InlineKeyboardButton("🔙 Volver", callback_data="volver_versiones")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"🎬 *{pelicula['titulo']}*\n\n¿Qué quieres hacer?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 📅 Función que maneja la selección de horarios
async def handle_ver_horarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Obtener la película seleccionada
    pelicula = context.user_data.get('pelicula_seleccionada')
    if not pelicula:
        await query.edit_message_text(text="❌ Error: No hay película seleccionada")
        return
    
    # Extraer días disponibles
    funciones = pelicula.get('funciones', [])
    if not funciones:
        await query.edit_message_text(text="❌ No hay horarios disponibles para esta película")
        return
    
    # Crear botones con los días
    keyboard = []
    for i, funcion in enumerate(funciones):
        dia = funcion['dia']
        keyboard.append([InlineKeyboardButton(f"📅 {dia}", callback_data=f"dia_{i}")])

    # Añadir botón volver
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_opciones")])

    # Guardar funciones para uso posterior
    context.user_data['funciones_actuales'] = funciones

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"🎬 *{pelicula['titulo']}*\n\n📅 Selecciona el día:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 📅 Función que maneja la selección de un día específico
async def handle_dia_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Extraer índice del día del callback_data
    dia_index = int(query.data.replace("dia_", ""))
    
    # Obtener la función específica del día
    funciones_actuales = context.user_data.get('funciones_actuales', [])
    funcion = funciones_actuales[dia_index]
    
    # Extraer horarios de ese día
    horarios = funcion.get('horarios', [])
    if not horarios:
        await query.edit_message_text(text="❌ No hay horarios disponibles para este día")
        return
    
    # Crear botones con los horarios (cada uno abre el link de compra)
    keyboard = []
    for horario in horarios:
        hora = horario['hora']
        url = horario['url']
        keyboard.append([InlineKeyboardButton(f"🕐 {hora}", url=url)])

    # Añadir botón volver
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_dias")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"🎬 *{context.user_data['pelicula_seleccionada']['titulo']}*\n📅 *{funcion['dia']}*\n\n🕐 Selecciona horario:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 📖 Función que maneja la solicitud de información de la película
async def handle_ver_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Obtener la película seleccionada
    pelicula = context.user_data.get('pelicula_seleccionada')
    if not pelicula:
        await query.edit_message_text(text="❌ Error: No hay película seleccionada")
        return
    
    # Obtener información básica
    titulo = pelicula['titulo']
    tiene_preventas = "✅ Sí" if pelicula['preventas'] else "❌ No"
    num_dias = len(pelicula.get('funciones', []))

    # Buscar información en TMDb
    pelicula_tmdb = buscar_pelicula(titulo)

    # Crear botón de volver
    keyboard = [
        [InlineKeyboardButton("🔙 Volver", callback_data="volver_opciones")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if pelicula_tmdb:
        # Información de TMDb disponible
        sinopsis = pelicula_tmdb.get('overview', 'No disponible')
        año = pelicula_tmdb.get('release_date', '')[:4] if pelicula_tmdb.get('release_date') else 'N/A'
        puntuacion = pelicula_tmdb.get('vote_average', 0)
        cartel_url = obtener_url_cartel(pelicula_tmdb.get('poster_path', ''))
        
        mensaje = f"""🎬 *{titulo}*

    📋 **Información:**
    - Año: {año}
    - Puntuación: ⭐ {puntuacion}/10
    - En preventa: {tiene_preventas}
    - Días disponibles: {num_dias}

    📝 **Sinopsis:**
    {sinopsis}"""

    # Si hay cartel, enviar como foto separada PRIMERO
    if cartel_url:
        # Eliminar imagen anterior si existe
        imagen_anterior_id = context.user_data.get('imagen_info_id')
        if imagen_anterior_id:
            try:
                await context.bot.delete_message(
                    chat_id=query.message.chat_id,
                    message_id=imagen_anterior_id
                )
            except:
                pass  # Ignorar si no se puede eliminar
        
        # Enviar nueva imagen
        mensaje_imagen = await query.message.reply_photo(
            photo=cartel_url,
            caption=f"🎬 *{titulo}*",
            parse_mode="Markdown"
        )
        
        # Guardar ID de la nueva imagen
        context.user_data['imagen_info_id'] = mensaje_imagen.message_id

    else:
        # No se encontró en TMDb
        mensaje = f"""🎬 *{titulo}*

    📋 **Información disponible:**
    - En preventa: {tiene_preventas}
    - Días disponibles: {num_dias}

    ❌ **No se encontró información adicional en TMDb**"""
    
    # DESPUÉS editar mensaje original con info y botón volver funcional
    await query.edit_message_text(
        text=mensaje,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 🔙 Función que maneja el botón de volver a las opciones
async def handle_volver_opciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Obtener la película seleccionada
    pelicula = context.user_data.get('pelicula_seleccionada')
    if not pelicula:
        await query.edit_message_text(text="❌ Error: No hay película seleccionada")
        return
    
    # Mostrar las opciones (horarios/info) con botón volver
    keyboard = [
        [InlineKeyboardButton("📅 Ver horarios", callback_data="ver_horarios")],
        [InlineKeyboardButton("📖 Ver información", callback_data="ver_info")]
    ]
    
    # Determinar a dónde volver según el contexto
    versiones_actuales = context.user_data.get('versiones_actuales', [])
    if versiones_actuales and len(versiones_actuales) > 1:
        # Si hay múltiples versiones, volver a versiones
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_versiones")])
    else:
        # Si hay una sola versión, volver a películas
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_peliculas")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"🎬 *{pelicula['titulo']}*\n\n¿Qué quieres hacer?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 🔙 Función que maneja el botón de volver a la selección de días
async def handle_volver_dias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Obtener la película seleccionada
    pelicula = context.user_data.get('pelicula_seleccionada')
    if not pelicula:
        await query.edit_message_text(text="❌ Error: No hay película seleccionada")
        return
    
    # Obtener funciones (ya están guardadas en el contexto)
    funciones = context.user_data.get('funciones_actuales', [])
    if not funciones:
        await query.edit_message_text(text="❌ No hay horarios disponibles")
        return
    
    # Recrear botones con los días
    keyboard = []
    for i, funcion in enumerate(funciones):
        dia = funcion['dia']
        keyboard.append([InlineKeyboardButton(f"📅 {dia}", callback_data=f"dia_{i}")])
    
    # Añadir botón volver
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_opciones")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"🎬 *{pelicula['titulo']}*\n\n📅 Selecciona el día:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 🔙 Función que maneja el botón de volver a la selección de películas
async def handle_volver_peliculas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Obtener datos guardados del contexto
    peliculas_agrupadas = context.user_data.get('peliculas_agrupadas', {})
    if not peliculas_agrupadas:
        await query.edit_message_text(text="❌ Error: No hay datos de películas")
        return
    
    # Recrear botones con títulos base únicos (igual que en handle_button_click)
    keyboard = []
    for titulo_base in peliculas_agrupadas:
        # Verificar si alguna versión tiene preventas
        tiene_preventas = any(pelicula['preventas'] for pelicula in peliculas_agrupadas[titulo_base])
        
        # Añadir indicador de preventa si es necesario
        texto_boton = f"🎬 {titulo_base}"
        if tiene_preventas:
            texto_boton += " (Preventa)"
        
        keyboard.append([InlineKeyboardButton(texto_boton, callback_data=f"pelicula_{texto_boton.replace('🎬 ', '')}")])
    
    # Añadir botón volver
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_cines")])
    
    # Determinar texto según el cine actual
    cine_actual = context.user_data.get('cine_actual', 'cinesa')
    textos_cine = {
        'cinesa': "🎟️ *Cinesa Parquesur* - Películas disponibles:",
        'yelmo': "🍿 *Yelmo Islazul* - Películas disponibles:",
        'odeon': "🎥 *Odeón Sambil* - Películas disponibles:"
    }
    texto_mensaje = textos_cine.get(cine_actual, "Películas disponibles:")
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=texto_mensaje,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 🔙 Función que maneja el botón de volver a la pantalla inicial de cines
async def handle_volver_cines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Recrear pantalla inicial con botones de cines (igual que en start)
    keyboard = [
        [
            InlineKeyboardButton("🎟️ Cinesa Parquesur", callback_data="cinesa"),
            InlineKeyboardButton("🎥 Odeón Sambil", callback_data="odeon"),
            InlineKeyboardButton("🍿 Yelmo Islazul", callback_data="yelmo"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="🎬 ¡Bienvenido al Bot de Cartelera de Madrid Sur!\n\n"
             "Selecciona un cine para ver la cartelera:",
        reply_markup=reply_markup
    )

# 🔙 Función que maneja el botón de volver a la selección de versiones
async def handle_volver_versiones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Obtener datos del contexto
    versiones_actuales = context.user_data.get('versiones_actuales', [])
    if not versiones_actuales:
        await query.edit_message_text(text="❌ Error: No hay datos de versiones")
        return
    
    # Obtener título base para el mensaje
    titulo_base = versiones_actuales[0]['titulo'].split('(')[0].strip()
    
    # Recrear botones de versiones
    keyboard = []
    for i, pelicula in enumerate(versiones_actuales):
        titulo_completo = pelicula['titulo']
        keyboard.append([InlineKeyboardButton(f"🎭 {titulo_completo}", callback_data=f"version_{i}")])
    
    # Añadir botón volver
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="volver_peliculas")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"🎬 *{titulo_base}*\n\nSelecciona la versión:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 🚀 Arranque del bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers de comandos y callbacks
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_movie_selection, pattern="^pelicula_"))
    app.add_handler(CallbackQueryHandler(handle_version_selection, pattern="^version_"))
    app.add_handler(CallbackQueryHandler(handle_ver_horarios, pattern="^ver_horarios$"))
    app.add_handler(CallbackQueryHandler(handle_ver_info, pattern="^ver_info$"))
    app.add_handler(CallbackQueryHandler(handle_volver_opciones, pattern="^volver_opciones$"))
    app.add_handler(CallbackQueryHandler(handle_volver_dias, pattern="^volver_dias$"))
    app.add_handler(CallbackQueryHandler(handle_volver_peliculas, pattern="^volver_peliculas$"))
    app.add_handler(CallbackQueryHandler(handle_volver_cines, pattern="^volver_cines$"))
    app.add_handler(CallbackQueryHandler(handle_volver_versiones, pattern="^volver_versiones$"))  
    app.add_handler(CallbackQueryHandler(handle_dia_selection, pattern="^dia_"))
    app.add_handler(CallbackQueryHandler(handle_button_click))
    
    print("🤖 Bot ejecutándose... Esperando interacciones")
    app.run_polling()

if __name__ == "__main__":
    main()