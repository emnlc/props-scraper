from selenium_driverless import webdriver
from collections import defaultdict

import asyncio

GAME_LINES = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

def convert_to_dict(d):
    if isinstance(d, defaultdict):
        return {k: convert_to_dict(v) for k, v in d.items()}
    elif isinstance(d, dict):
        return {k: convert_to_dict(v) for k, v in d.items()}
    else:
        return d
    
def shorten_market(market):
    if market == "3 Point FG Made":
        return "3PT"
    elif market == "Assists":
        return "AST"
    elif market == "Blocks":
        return "BLK"
    elif market == "Points":
        return "PTS"
    elif market == "Pts + Ast":
        return "PA"
    elif market == "Pts + Reb":
        return "PR"
    elif market == "Pts + Reb + Ast":
        return "PRA"
    elif market == "Reb + Ast":
        return "RA"
    elif market == "Rebounds":
        return "REB"
    elif market == "Steals":
        return "STL"
    

async def scraper():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    async with webdriver.Chrome(options=options) as browser:
        print("getting ready to scrape. . .")
        # open the target website
        await browser.get("https://www.sportsgrid.com/nba/player-props")
        # implicitly wait for the page to load
        await browser.sleep(5)
        
        # personal data consent form
        try:
            consent_form = await browser.find_element("css selector", "div.fc-consent-root")
            consenst_button = await consent_form.find_element("xpath", "./div[2]//div[2]//div[2]//button[2]")
            await consenst_button.click()
            await browser.sleep(5)
        except Exception as _:
            pass
        
        main_container = await browser.find_element("css selector", "main.site-main div")
        
        try:
            # ensure props are available
            await main_container.find_element("xpath", "./div[3]//div//button")
        except Exception as _:
            print("No data yet. . .")
            return
        
        button = await main_container.find_element("xpath", "./div[3]//div//button")
        await button.click()
        await browser.sleep(5)
        
        table = await main_container.find_element("xpath", "./div[2]")
        
        rows = await table.find_elements("css selector", "div.desk-view")
        # print(f"{len(rows)} total props found!")
        for _, row in enumerate(rows):
            await browser.sleep(1)
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