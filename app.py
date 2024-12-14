from fastapi import FastAPI
from fastapi_utilities import repeat_every
from prizepicks import get_prizepicks
import dotenv
import os

app = FastAPI()
dotenv.load_dotenv()
PRIZE_PICKS_CACHE = {}

@app.on_event("startup")
@repeat_every(seconds=120) 
async def update_prizepicks():
    api_url = os.getenv("API_URL")

    global PRIZE_PICKS_CACHE
    PRIZE_PICKS_CACHE = get_prizepicks(api_url=api_url)
    
    return PRIZE_PICKS_CACHE

@app.get("/api/prizepicks/nba")
def read_game_lines():
    return PRIZE_PICKS_CACHE  # return current cache

#############################
# FOR LOCAL DEVELOPMENT ONLY #
#############################
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8080)