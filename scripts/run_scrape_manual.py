import asyncio
from src.scheduler.jobs import scraping_job
from src.database.engine import init_db
from src.utils.logging import setup_logging

async def run_scrape():
    setup_logging()
    await init_db()
    print("Iniciando scraping job manual...")
    stats = await scraping_job()
    print(f"Resultado: {stats}")

if __name__ == "__main__":
    asyncio.run(run_scrape())
