import asyncio
import requests
from src.scraper.pdf_parser import PDFParser

async def test_specific_pdf(url):
    print(f"Probando PDF: {url}")
    parser = PDFParser()
    response = requests.get(url)
    if response.status_code == 200:
        comp = parser.parse(response.content, name="Test", pdf_url=url)
        print(f"Competición: {comp.name}")
        print(f"Lugar: {comp.location}")
        found_times = 0
        for event in comp.events:
            time_str = event.scheduled_time.strftime("%H:%M") if event.scheduled_time else "SIN HORA"
            if event.scheduled_time:
                found_times += 1
            print(f"  - {event.discipline} ({event.sex}): {time_str}")
        print(f"\nTotal pruebas: {len(comp.events)}, Pruebas con hora: {found_times}")
    else:
        print(f"Error descargando: {response.status_code}")

if __name__ == "__main__":
    # URL de Jornada Menores 11/01
    url = "https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/jornadamenores_gallur_2026_01_11.pdf?215752"
    asyncio.run(test_specific_pdf(url))
