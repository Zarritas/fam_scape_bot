"""
Teclados inline para el bot.

Define los teclados interactivos para selección de pruebas,
suscripciones, etc.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_event_type_keyboard() -> InlineKeyboardMarkup:
    """Teclado para seleccionar tipo de prueba: Carreras o Concursos."""
    keyboard = [
        [
            InlineKeyboardButton("🏃 Carreras", callback_data="type:carrera"),
            InlineKeyboardButton("🎯 Concursos", callback_data="type:concurso"),
        ],
        [
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_track_events_keyboard() -> InlineKeyboardMarkup:
    """Teclado para seleccionar prueba de pista (carreras)."""
    keyboard = [
        [
            InlineKeyboardButton("60m", callback_data="disc:60"),
            InlineKeyboardButton("100m", callback_data="disc:100"),
            InlineKeyboardButton("200m", callback_data="disc:200"),
        ],
        [
            InlineKeyboardButton("400m", callback_data="disc:400"),
            InlineKeyboardButton("800m", callback_data="disc:800"),
            InlineKeyboardButton("1500m", callback_data="disc:1500"),
        ],
        [
            InlineKeyboardButton("3000m", callback_data="disc:3000"),
            InlineKeyboardButton("5000m", callback_data="disc:5000"),
            InlineKeyboardButton("10000m", callback_data="disc:10000"),
        ],
        [
            InlineKeyboardButton("60m Vallas", callback_data="disc:60 Vallas"),
            InlineKeyboardButton("100m Vallas", callback_data="disc:100 Vallas"),
        ],
        [
            InlineKeyboardButton("110m Vallas", callback_data="disc:110 Vallas"),
            InlineKeyboardButton("400m Vallas", callback_data="disc:400 Vallas"),
        ],
        [
            InlineKeyboardButton("3000m Obstáculos", callback_data="disc:3000 Obstáculos"),
        ],
        [
            InlineKeyboardButton("4x100m", callback_data="disc:4x100"),
            InlineKeyboardButton("4x400m", callback_data="disc:4x400"),
        ],
        [
            InlineKeyboardButton("⬅️ Volver", callback_data="back:type"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_field_events_keyboard() -> InlineKeyboardMarkup:
    """Teclado para seleccionar prueba de campo (concursos)."""
    keyboard = [
        [
            InlineKeyboardButton("Altura", callback_data="disc:Altura"),
            InlineKeyboardButton("Pértiga", callback_data="disc:Pértiga"),
        ],
        [
            InlineKeyboardButton("Longitud", callback_data="disc:Longitud"),
            InlineKeyboardButton("Triple Salto", callback_data="disc:Triple Salto"),
        ],
        [
            InlineKeyboardButton("Peso", callback_data="disc:Peso"),
            InlineKeyboardButton("Disco", callback_data="disc:Disco"),
        ],
        [
            InlineKeyboardButton("Martillo", callback_data="disc:Martillo"),
            InlineKeyboardButton("Jabalina", callback_data="disc:Jabalina"),
        ],
        [
            InlineKeyboardButton("⬅️ Volver", callback_data="back:type"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_sex_keyboard(discipline: str) -> InlineKeyboardMarkup:
    """Teclado para seleccionar sexo de la prueba."""
    keyboard = [
        [
            InlineKeyboardButton("👨 Masculino", callback_data=f"sex:{discipline}:M"),
            InlineKeyboardButton("👩 Femenino", callback_data=f"sex:{discipline}:F"),
        ],
        [
            InlineKeyboardButton("👥 Ambos", callback_data=f"sex:{discipline}:B"),
        ],
        [
            InlineKeyboardButton("⬅️ Volver", callback_data="back:disc"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_subscriptions_keyboard(subscriptions: list) -> InlineKeyboardMarkup:
    """
    Teclado con lista de suscripciones para desuscribirse.
    
    Args:
        subscriptions: Lista de objetos Subscription
    """
    keyboard = []
    
    for sub in subscriptions:
        sex_label = "👨 M" if sub.sex == "M" else "👩 F"
        text = f"❌ {sub.discipline} {sex_label}"
        callback = f"unsub:{sub.discipline}:{sub.sex}"
        keyboard.append([InlineKeyboardButton(text, callback_data=callback)])
    
    keyboard.append([
        InlineKeyboardButton("🔙 Cerrar", callback_data="cancel"),
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_confirm_keyboard(action: str, data: str) -> InlineKeyboardMarkup:
    """Teclado de confirmación para acciones críticas."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm:{action}:{data}"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_confirm_scrape_keyboard() -> InlineKeyboardMarkup:
    """Teclado de confirmación para force_scrape."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Ejecutar ahora", callback_data="admin:scrape:confirm"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
