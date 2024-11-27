from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scraper import get_game_lines, convert_to_dict
import asyncio
import uvicorn

GAME_LINES_CACHE = {}
scheduler = BackgroundScheduler()

app = FastAPI()

async def update_game_lines_cache():
    global GAME_LINES_CACHE
    
    try:
        print("updating game lines...")

        new_data = await get_game_lines()
        GAME_LINES_CACHE = convert_to_dict(new_data)
        
        print("game lines cache updated")
    except Exception as e:
        print(f"Error updating game lines cache: {e}")

def sync_update_game_lines_cache():
    asyncio.run(update_game_lines_cache())

@app.on_event("startup")
async def startup_event():
    print("Performing initial game lines scrape on startup...")
    await update_game_lines_cache()
    
    scheduler.add_job(
        sync_update_game_lines_cache,
        trigger=IntervalTrigger(minutes=5),
        id="game_lines_scraper",
        replace_existing=True
    )
    
    scheduler.start()
    print("scheduler started.")
    
@app.on_event("shutdown")
def shutdown_event():
    print("stopping scheduler. . .")
    scheduler.shutdown()

@app.get("/api/nba")
async def read_game_lines():
    return GAME_LINES_CACHE # return current cache

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)