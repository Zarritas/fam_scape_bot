from io import BytesIO

import pdfplumber
import requests

url = "https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/copaabsoluta_gallur_2026_01_10.pdf?215752"
response = requests.get(url)
if response.status_code == 200:
    with pdfplumber.open(BytesIO(response.content)) as pdf:
        text = pdf.pages[0].extract_text()
        print("--- Texto ---")
        print(text[:500])
else:
    print(f"Error {response.status_code}")
