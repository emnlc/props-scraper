from fastapi import FastAPI
import asyncio
import uvicorn
from scraper import get_game_lines, convert_to_dict

GAME_LINES_CACHE = {}

app = FastAPI()

# Background task to run scraper periodically
async def run_scraper_periodically():
    global GAME_LINES_CACHE
    while True:
        print("running scraper...")
        try:
            GAME_LINES_CACHE = convert_to_dict(await get_game_lines())
            print("LINES UPDATED")
        except Exception as e:
            print(f"Error while running scraper: {e}")
        await asyncio.sleep(300)  # Run every 5

@app.on_event("startup")
async def startup_event():
    global GAME_LINES_CACHE
    print("startup scraping...")
    GAME_LINES_CACHE = convert_to_dict(await get_game_lines())
    
    asyncio.create_task(run_scraper_periodically())

@app.get("/api/nba")
async def read_game_lines():
    return GAME_LINES_CACHE

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)