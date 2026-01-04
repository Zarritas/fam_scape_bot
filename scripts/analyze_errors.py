import asyncio
from src.database.engine import get_session_factory
from src.database.repositories import ErrorRepository

async def analyze_errors():
    session_factory = get_session_factory()
    async with session_factory() as session:
        error_repo = ErrorRepository(session)
        # Obtener todos los errores para probar
        errors = await error_repo.get_all()
        # Limitar manualmente a los últimos 20 si hay muchos
        errors = sorted(errors, key=lambda x: x.timestamp, reverse=True)[:20]
        
        print(f"--- Análisis de {len(errors)} errores recientes ---")
        for error in errors:
            print(f"\n[{error.timestamp}] {error.component} | {error.error_type}")
            print(f"Mensaje: {error.message}")
            if error.stack_trace:
                # Mostrar solo las últimas 3 líneas del stack trace para no saturar
                lines = error.stack_trace.strip().split("\n")
                print("Stack (últimas líneas):")
                for line in lines[-3:]:
                    print(f"  {line}")
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(analyze_errors())
