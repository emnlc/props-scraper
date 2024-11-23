from flask import Flask, jsonify
from scraper import get_game_lines, convert_to_dict
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

GAME_LINES_CACHE = {}

def fetch_game_lines():
    global GAME_LINES_CACHE
    data = get_game_lines()
    GAME_LINES_CACHE = convert_to_dict(data)

@app.route('/api/nba', methods=['GET'])
def game_lines():
    # Convert to regular dict
    return jsonify(GAME_LINES_CACHE)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_game_lines, "interval", minutes=15)
    scheduler.start()
    
    fetch_game_lines()
    
    # Run the Flask app
    try:
        app.run(debug=True, host='0.0.0.0')
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()