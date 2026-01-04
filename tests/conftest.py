"""
Configuración global de pytest y fixtures compartidos.
"""

import os
import pytest
from pathlib import Path

# Establecer variables de entorno para tests antes de importar config
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_token_12345")
os.environ.setdefault("ADMIN_USER_ID", "123456789")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("LOG_FORMAT", "text")


@pytest.fixture
def fixtures_dir() -> Path:
    """Directorio de fixtures para tests."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_calendar_html() -> str:
    """HTML de ejemplo del calendario FAM."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Calendario - FAM</title></head>
    <body>
        <div class="item-page">
            <h1>Calendario de Competiciones</h1>
            <table>
                <tr>
                    <td>11 de enero</td>
                    <td>
                        <a href="/files/convocatoria_2026_01.pdf">
                            Control de Pista Cubierta
                        </a>
                    </td>
                    <td>Gallur</td>
                </tr>
                <tr>
                    <td>18 de enero</td>
                    <td style="background-color: yellow;">
                        <a href="/files/convocatoria_2026_02.pdf">
                            Campeonato de Madrid Sub20
                        </a>
                    </td>
                    <td>Vallehermoso</td>
                </tr>
                <tr>
                    <td>25 de enero</td>
                    <td>
                        <a href="https://www.atletismomadrid.com/files/meeting.pdf">
                            Meeting de Invierno
                        </a>
                    </td>
                    <td>Moratalaz</td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_events_table() -> list[list[str]]:
    """Tabla de pruebas de ejemplo."""
    return [
        ["Prueba", "Sexo", "Hora", "Categoría"],
        ["60m", "M", "10:00", "Senior"],
        ["60m", "F", "10:15", "Senior"],
        ["200m", "M", "10:30", "Senior"],
        ["Altura", "F", "11:00", "Sub23"],
        ["Pértiga", "M", "11:30", "Absoluto"],
        ["Peso", "F", "12:00", "Senior"],
    ]


@pytest.fixture
def sample_pdf_text() -> str:
    """Texto de ejemplo extraído de un PDF."""
    return """
    FEDERACIÓN DE ATLETISMO DE MADRID
    
    CONTROL DE PISTA CUBIERTA
    
    Fecha: 11 de enero de 2026
    Lugar: Polideportivo Gallur
    
    PROGRAMA DE PRUEBAS
    
    CARRERAS
    
    10:00 - 60m masculino
    10:15 - 60m femenino  
    10:30 - 200m masculino
    10:45 - 200m femenino
    11:00 - 400m masculino
    11:15 - 400m femenino
    
    CONCURSOS
    
    10:00 - Altura femenino
    10:30 - Pértiga masculino
    11:00 - Longitud masculino
    11:30 - Peso femenino
    """
