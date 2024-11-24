from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium_driverless import webdriver
from collections import defaultdict

import asyncio
import random

GAME_LINES = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

MARKET_SHORTEN = {
    "3 Point FG Made": "3PT",
    "Assists": "AST",
    "Blocks": "BLK",
    "Points": "PTS",
    "Pts + Ast": "PA",
    "Pts + Reb": "PR",
    "Pts + Reb + Ast": "PRA",
    "Reb + Ast": "RA",
    "Rebounds": "REB",
    "Steals": "STL",
}

DELAY = random.uniform(5, 10)

def convert_to_dict(d):
    if isinstance(d, defaultdict):
        return {k: convert_to_dict(v) for k, v in d.items()}
    elif isinstance(d, dict):
        return {k: convert_to_dict(v) for k, v in d.items()}
    else:
        return d
    
def shorten_market(market):
    return MARKET_SHORTEN.get(market, market)
    
async def scraper():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    async with webdriver.Chrome(options=options) as browser:
        print("getting ready to scrape. . .")
        # open the target website
        await browser.get("https://www.sportsgrid.com/nba/player-props", timeout=60)
        await browser.sleep(DELAY)
        
        # CONSENT FORM
        try:
            consent_form = await WebDriverWait(browser, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.fc-consent-root"))
            )
            
            consenst_button = await WebDriverWait(consent_form, 15).until(
                EC.presence_of_element_located((By.XPATH, "./div[2]//div[2]//div[2]//button[2]"))
            )
            
            await consenst_button.click()
            await browser.sleep(DELAY)
        except Exception as _:
            print("no form found")
        
        # MAIN CONTAINER 
        try:
            main_container = await WebDriverWait(browser, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main.site-main div"))
            )
        except asyncio.TimeoutError:
            print("Timeout searching for main container")
            return
        
        # LOAD BUTTON
        try:
            button = await main_container.find_element("xpath", "./div[3]//div//button")
            await button.click()
        except Exception as _:
            print("No button found or no data available.")
            return
        
        table = await main_container.find_element("xpath", "./div[2]")        
        rows = await table.find_elements("css selector", "div.desk-view")
        print(f"{len(rows)} total props found!")
        
        for _, row in enumerate(rows):
            await browser.sleep(random.uniform(0.5, 1))
            row_data = await row.find_element("css selector", "div div div div div")
            
            # game title
            teams_container = await row_data.find_element("css selector", "div.team-details div")
            away_team_element = await teams_container.find_element("xpath", "./div[1]//span")
            home_team_element = await teams_container.find_element("xpath", "./div[3]//span")
            away_team = await away_team_element.text
            home_team = await home_team_element.text
            game_title = away_team + " " + home_team
            
            # player name
            player_name_element = await row_data.find_element("css selector", "div.player-details a div div p")
            player_name = await player_name_element.text
            
            # market
            market_element = await row_data.find_element("css selector", "div.market-details div p")
            market_description = await market_element.text
            market_description_array = str(market_description).split()
            line = market_description_array[0]
            market = shorten_market(" ".join(market_description_array[1:]))
            
            GAME_LINES[game_title][market][player_name]["line"] = line
    print("scraping finished!")
    
def get_game_lines():
    asyncio.run(scraper())
    return GAME_LINES
