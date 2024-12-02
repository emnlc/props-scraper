from fastapi import FastAPI
from fastapi_utilities import repeat_every
from scraper import scraper
import datetime

app = FastAPI()

GAME_LINES_CACHE = {}

@app.on_event("startup")
@repeat_every(seconds=600) # update GAME_LINES_CACHE every 10 minutes
async def update_game_lines():
    global GAME_LINES_CACHE
    print("Updating game lines. . .")
    
    new_data = await scraper()
    
    if new_data:
        GAME_LINES_CACHE = new_data

    print(f"Updated game lines at {datetime.datetime.now()}")

@app.get("/api/nba")
def read_game_lines():
    return GAME_LINES_CACHE  # return current cache

##############################
# FOR LOCAL DEVELOPMENT ONLY #
##############################
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8080)