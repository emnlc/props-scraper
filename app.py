from fastapi import FastAPI
from fastapi_utilities import repeat_every
from scraper import scraper
import datetime
from asyncio import Lock

scrape_lock = Lock()
app = FastAPI()

GAME_LINES_CACHE = {}

@app.on_event("startup")
@repeat_every(seconds=600) # update GAME_LINES_CACHE every 10 minutes
async def update_game_lines():
    global GAME_LINES_CACHE
    
    if scrape_lock.locked():
        print("Scraper still runninng skipping this interval. . .")
        return GAME_LINES_CACHE
    
    async with scrape_lock:
        new_data = await scraper()
    
        if new_data:
            GAME_LINES_CACHE = new_data

    print(f"Updated game lines at {datetime.datetime.now()}")
    return GAME_LINES_CACHE

@app.get("/api/nba")
def read_game_lines():
    return GAME_LINES_CACHE  # return current cache

#############################
# FOR LOCAL DEVELOPMENT ONLY #
#############################
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)