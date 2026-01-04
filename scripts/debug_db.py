import asyncio
import sqlite3

from src.config import settings


async def debug_db():
    print(f"DATABASE_URL: {settings.database_url}")

    # Extraer el path del archivo si es sqlite
    if settings.is_sqlite:
        path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        print(f"Path detectado: {path}")

        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()

            # Verificar tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tablas encontradas: {tables}")

            if ("error_logs",) in tables:
                cursor.execute("PRAGMA table_info(error_logs);")
                info = cursor.fetchall()
                print("Estructura de error_logs:")
                for col in info:
                    print(f"  {col}")

            conn.close()
        except Exception as e:
            print(f"Error conectando con sqlite3: {e}")


if __name__ == "__main__":
    asyncio.run(debug_db())
