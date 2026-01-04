import asyncio
import logging

from src.scraper.web_scraper import WebScraper

# Configurar logging para ver resultados
logging.basicConfig(level=logging.INFO)


async def test_scraping():
    print("Iniciando prueba de scraping...")
    scraper = WebScraper()

    # Probar con el mes de enero 2026 (mes del ejemplo del usuario)
    try:
        competitions = scraper.get_competitions(1, 2026)
        print(f"\nSe encontraron {len(competitions)} competiciones:")
        for i, comp in enumerate(competitions):
            if comp.has_modifications or "Mundo" in comp.name:
                print(f"!!! DESTACADA Encontrada: {comp.name}")
                print(f"    Modificaciones: {comp.has_modifications}")
                print(f"    Fecha: {comp.date_str}")
                print(f"    Tipo: {comp.competition_type}")
                print(f"    PDF: {comp.pdf_url}")
            elif i < 10:
                print(f"- {comp.name} ({comp.date_str}) [{comp.competition_type}]")

    except Exception as e:
        print(f"Error durante el scraping: {e}")


if __name__ == "__main__":
    asyncio.run(test_scraping())
