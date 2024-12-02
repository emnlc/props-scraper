from selenium_driverless import webdriver
from collections import defaultdict
import random

MARKET_SHORTEN = {
    "Points": "PTS",
    "Rebounds": "REB",
    "Assists": "AST",
    "3 Point FG Made": "3PT",
    "Pts + Ast": "PA",
    "Pts + Reb": "PR",
    "Reb + Ast": "RA",
    "Pts + Reb + Ast": "PRA",
    "Blocks": "BLK",
    "Turnovers": "TO",
    "Stl + Blk": "SB",
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
    GAME_LINES = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    async with webdriver.Chrome(options=options) as browser:
        print("getting ready to scrape. . .")
        # open the target website
        await browser.get("https://www.sportsgrid.com/nba/player-props", timeout=60)
        await browser.sleep(DELAY)
        
        # CONSENT FORM
        try:
            consent_form = await browser.find_element("css selector", "div.fc-consent-root")
            consent_button = await consent_form.find_element("xpath", "./div[2]//div[2]//div[2]//button[2]")
            
            await consent_button.click()
            await browser.sleep(DELAY)
        except Exception as _:
            print("no form found")

        # TARGET DRAFTKINGS IF POSSIBLE
        try:
            filter_container = await browser.find_element("css selector", "div.style_sidebarContainer___e2rA div div div div")
            await filter_container.click()
            await browser.sleep(DELAY)
            
            sportsbook_options_button = await browser.find_element("css selector", "div.dropdownContainer")
            await sportsbook_options_button.click()
            await browser.sleep(DELAY)
            
            draftkings_button = await sportsbook_options_button.find_element("xpath", "..//ul//li[1]")
            await draftkings_button.click()
            await browser.sleep(DELAY)
            print("Now using DraftKings lines")
            
            back_button_container = await browser.find_element("css selector", "div.style_sidebarContainer___e2rA div")
            back_button = await back_button_container.find_element("xpath", "./div[2]//div[1]//div")

            await back_button.click()
            await browser.sleep(DELAY)
        except Exception as _:
            print("Couldn't load DraftKings lines, staying with FanDuel lines.")
        
        # MAIN CONTAINER 
        try:
            main_container = await browser.find_element("css selector", "main.site-main div")
        except Exception as _:
            print("Timeout searching for main container")
            return {}
        
        # LOAD MORE BUTTON
        try:
            button = await main_container.find_element("xpath", "./div[3]//div//button")
            await button.click()
        except Exception as _:
            print("No button found or no data available.")
            return {}
        
        table = await main_container.find_element("xpath", "./div[2]")        
        rows = await table.find_elements("css selector", "div.desk-view")
        print(f"{len(rows)} total props found!")
        GAME_LINES["total_count"] = len(rows)
        for _, row in enumerate(rows):
            await browser.sleep(random.uniform(0.1, 0.5))
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
            
            GAME_LINES[game_title][player_name][market] = line

    print("scraping finished!")
    return convert_to_dict(GAME_LINES)
