import pdfplumber
import requests
from io import BytesIO

url = "https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/jornadamenores_gallur_2026_01_11.pdf?215752"
response = requests.get(url)
if response.status_code == 200:
    with pdfplumber.open(BytesIO(response.content)) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"--- Página {i+1} ---")
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                print(f"Tabla {j+1}:")
                for row in table:
                    print(f"  {row}")
else:
    print(f"Error {response.status_code}")
