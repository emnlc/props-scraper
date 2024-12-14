import requests
from datetime import datetime
from collections import defaultdict

def get_prizepicks(api_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return None

    data = response.json()
    
    # Step 1: Map player IDs to details
    players = {
        item['id']: {
            "team_abbr": item['attributes'].get("team"),
            "player_name": item['attributes'].get("display_name"),
            "headshot": item['attributes'].get("image_url"),
        }
        for item in data.get('included', [])
        if item.get('type') == 'new_player' and not item['attributes'].get("combo", False)
    }

    # Step 2: Organize props into games
    formatted_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    for item in data.get('data', []):
        if item.get('type') != 'projection':
            continue

        relationships = item.get('relationships', {})
        player_id = relationships.get('new_player', {}).get('data', {}).get('id')
        if not player_id or player_id not in players:
            continue

        # Extract player and prop info
        player_info = players[player_id]
        team_abbr = player_info['team_abbr']
        player_name = player_info['player_name']
        start_time = item.get('attributes', {}).get('start_time')
        opponent_team = item.get('attributes', {}).get('description')

        if not (start_time and opponent_team):
            continue

        # Create game key
        game_date = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%b %d")
        game_teams = sorted([team_abbr, opponent_team])
        game_key = f"{game_teams[0]} {game_teams[1]} {game_date}"

        # Initialize player entry and add props
        player_entry = formatted_data[game_key][team_abbr].setdefault(player_name, {
            'props': [],
            'headshot': player_info["headshot"],
            'player_id': player_id
        })
        player_entry['props'].append({
            'prop_id': item.get('id'),
            'details': item.get('attributes', {}),
            'related_stat': relationships.get('stat_average', {}).get('data', {})
        })

    return formatted_data
