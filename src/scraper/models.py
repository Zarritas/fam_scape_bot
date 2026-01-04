"""
Modelos de datos para el scraper.

Dataclasses que representan la información extraída del calendario
y los PDFs de la Federación de Atletismo de Madrid.
"""

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


class EventType(str, Enum):
    """Tipo de prueba atlética."""

    CARRERA = "carrera"
    CONCURSO = "concurso"


class Sex(str, Enum):
    """Sexo/categoría de la prueba."""

    MASCULINO = "M"
    FEMENINO = "F"


@dataclass
class RawCompetition:
    """
    Datos de una competición extraídos del calendario web.

    Representa la información básica antes de parsear el PDF.
    """

    name: str
    date_str: str  # Fecha como string (ej: "11 de enero" o "03/01")
    pdf_url: str
    has_modifications: bool = False  # Si tiene fondo amarillo/verde
    location: str | None = None
    competition_type: str | None = None  # Tipo: PC, AL, C, M, R, etc.

    def __post_init__(self) -> None:
        # Asegurar URL absoluta
        if self.pdf_url and not self.pdf_url.startswith("http"):
            from src.config import settings

            self.pdf_url = f"{settings.fam_base_url}{self.pdf_url}"


@dataclass
class Event:
    """
    Prueba individual dentro de una competición.

    Representa una prueba específica (ej: 400m masculino).
    """

    discipline: str  # Ej: "400", "Pértiga", "Altura"
    event_type: EventType  # carrera o concurso
    sex: Sex
    category: str = ""  # Ej: "Senior", "Sub23", "Juvenil"
    scheduled_time: time | None = None  # Hora programada (nullable)

    @property
    def display_name(self) -> str:
        """Nombre para mostrar: 'Disciplina Sexo'."""
        sex_label = "Masculino" if self.sex == Sex.MASCULINO else "Femenino"
        return f"{self.discipline} {sex_label}"

    @property
    def subscription_key(self) -> str:
        """Clave única para suscripciones: 'disciplina_sexo'."""
        return f"{self.discipline.lower()}_{self.sex.value}"


@dataclass
class Competition:
    """
    Competición completa con todos sus datos parseados.

    Incluye información del PDF y lista de pruebas.
    """

    name: str
    competition_date: date
    location: str
    pdf_url: str
    pdf_hash: str | None = None
    has_modifications: bool = False
    competition_type: str | None = None
    events: list[Event] = field(default_factory=list)

    def get_events_by_type(self, event_type: EventType) -> list[Event]:
        """Filtra pruebas por tipo (carrera/concurso)."""
        return [e for e in self.events if e.event_type == event_type]

    def get_events_by_sex(self, sex: Sex) -> list[Event]:
        """Filtra pruebas por sexo."""
        return [e for e in self.events if e.sex == sex]

    def get_events_by_discipline(self, discipline: str) -> list[Event]:
        """Busca pruebas por disciplina (búsqueda parcial, case-insensitive)."""
        discipline_lower = discipline.lower()
        return [e for e in self.events if discipline_lower in e.discipline.lower()]


# Mapeo de disciplinas conocidas para normalización
DISCIPLINE_ALIASES: dict[str, str] = {
    # Carreras
    "60 m": "60",
    "60m": "60",
    "100 m": "100",
    "100m": "100",
    "200 m": "200",
    "200m": "200",
    "400 m": "400",
    "400m": "400",
    "800 m": "800",
    "800m": "800",
    "1500 m": "1500",
    "1500m": "1500",
    "3000 m": "3000",
    "3000m": "3000",
    "5000 m": "5000",
    "5000m": "5000",
    "10000 m": "10000",
    "10000m": "10000",
    "60 m vallas": "60 Vallas",
    "60m vallas": "60 Vallas",
    "100 m vallas": "100 Vallas",
    "100m vallas": "100 Vallas",
    "110 m vallas": "110 Vallas",
    "110m vallas": "110 Vallas",
    "400 m vallas": "400 Vallas",
    "400m vallas": "400 Vallas",
    "3000 m obstáculos": "3000 Obstáculos",
    "4x100 m": "4x100",
    "4x100m": "4x100",
    "4x400 m": "4x400",
    "4x400m": "4x400",
    # Concursos
    "salto de altura": "Altura",
    "altura": "Altura",
    "salto de longitud": "Longitud",
    "longitud": "Longitud",
    "triple salto": "Triple Salto",
    "salto con pértiga": "Pértiga",
    "pértiga": "Pértiga",
    "pertiga": "Pértiga",
    "lanzamiento de peso": "Peso",
    "peso": "Peso",
    "lanzamiento de disco": "Disco",
    "disco": "Disco",
    "lanzamiento de martillo": "Martillo",
    "martillo": "Martillo",
    "lanzamiento de jabalina": "Jabalina",
    "jabalina": "Jabalina",
}


def normalize_discipline(discipline: str) -> str:
    """
    Normaliza el nombre de una disciplina.

    Convierte variantes como "60 m" o "60m" a un formato estándar.
    """
    discipline_lower = discipline.strip().lower()
    return DISCIPLINE_ALIASES.get(discipline_lower, discipline.strip())


# Categorías conocidas
KNOWN_CATEGORIES: list[str] = [
    "Sub10",
    "Sub12",
    "Sub14",
    "Sub16",
    "Sub18",
    "Sub20",
    "Sub23",
    "Senior",
    "Master",
    "Absoluto",
]


def detect_event_type(discipline: str) -> EventType:
    """
    Detecta si una disciplina es carrera o concurso.
    """
    concurso_keywords = [
        "altura",
        "longitud",
        "triple",
        "pértiga",
        "pertiga",
        "peso",
        "disco",
        "martillo",
        "jabalina",
        "salto",
    ]
    discipline_lower = discipline.lower()

    for keyword in concurso_keywords:
        if keyword in discipline_lower:
            return EventType.CONCURSO

    return EventType.CARRERA
