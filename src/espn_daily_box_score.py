#read html from url

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime
import gspread
from google.oauth2.service_account import Credentials
import logging
import os


# Set up logging with a relative path
log_file_path = os.path.join(os.path.dirname(__file__), 'logs', 'espn_daily_box_score_scraper.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO)

def get_daily_game_ids():
    yesterday_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')

    print("yesterday_date: ", yesterday_date)
    url = 'https://www.espn.com/wnba/scoreboard/_/date/' + yesterday_date
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
    response = requests.get(url, headers=headers)
    print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements with the class = AnchorLink Button Button--sm Button--anchorLink Button--alt mb4 w-100 mr2
    game_links = soup.find_all('a', class_='AnchorLink Button Button--sm Button--anchorLink Button--alt mb4 w-100 mr2')

    
    # Extract the game IDs from the href attribute of each anchor tag
    game_ids = []
    for link in game_links:
        href = link['href']
        # Extract game ID using a regular expression
        match = re.search(r'gameId/(\d+)', href)
        if match:
            game_id = match.group(1)
            game_ids.append(game_id)
    
    #remove duplicates from game_ids
    game_ids = list(set(game_ids))
    
    print("game_ids: ", game_ids)
    logging.info(f"Game IDs for {yesterday_date}: {game_ids}")
    return game_ids, yesterday_date

def get_box_score(game_ids, yesterday_date):
    # Convert yesterday_date to 'YYYY-MM-DD' format
    formatted_date = datetime.datetime.strptime(yesterday_date, '%Y%m%d').strftime('%Y-%m-%d')

    # Create an empty DataFrame to store the box score data
    box_scores = []

    # Iterate over each game ID
    for game_id in game_ids:
        url = f'https://www.espn.com/wnba/boxscore?gameId={game_id}'
        tables = pd.read_html(url, flavor='html5lib')
        box_score = tables[0]
        
        # Extract the necessary columns for quarter scores
        # Assuming the box score table is structured with team names in the first column and quarter scores in subsequent columns
        row_data = {
            'date': formatted_date,
            'game_id': game_id,
            'away_team': box_score.iloc[0, 0],
            'home_team': box_score.iloc[1, 0],
            'away_1q': box_score.iloc[0, 1],
            'home_1q': box_score.iloc[1, 1],
            'away_2q': box_score.iloc[0, 2],
            'home_2q': box_score.iloc[1, 2],
            'away_3q': box_score.iloc[0, 3],
            'home_3q': box_score.iloc[1, 3],
            'away_4q': box_score.iloc[0, 4],
            'home_4q': box_score.iloc[1, 4]
        }
        #df = df.append(row_data, ignore_index=True)
        box_scores.append(row_data)
        print(box_score)
        logging.info(f"Box score for game ID {game_id} added to DataFrame")

    df = pd.DataFrame(box_scores)
    return df
# Away Team,	Home Team,	Away 1st Q,	Home 1st Q
def append_to_google_sheet(df, credentials_path):
    try:
        # Specify the required scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        # Use Google API client library for authentication and sheet access
        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=scopes
        )
        gc = gspread.authorize(credentials)

        # Replace with your actual sheet URL and name
        sheet = gc.open_by_key('1Y7xom2jOLWYLzDlLsVYWZngs0JnnHjw5zZ7mR6GMjkQ').worksheet('2024_scores')

        # Append the data to the Google Sheet
        sheet.append_rows(df.values.tolist())
        

        print("Data appended to Google Sheet successfully!")
        logging.info("Data appended to Google Sheet successfully!")

    except Exception as e:
        print(f"Error appending data: {e}")
        logging.info(f"Error appending data: {e}")

def main():
    """
    Main function to execute data scraping and Google Sheet update.
    """
    print("Running")

    game_ids, yesterday_date = get_daily_game_ids()

    print("running get_box_score")
    box_scores = get_box_score(game_ids, yesterday_date)

    # Update credentials path here (replace with your actual path)
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'credentials.json')
    
    # Print the credentials path to debug
    print(f"Credentials path: {credentials_path}")
    logging.info(f"Credentials path: {credentials_path}")  

    # Print the credentials path to debug
    print(f"Credentials path: {credentials_path}")
    logging.info(f"Credentials path: {credentials_path}")

    # Print current working directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")

    # List files in the current directory
    print(f"Files in current directory: {os.listdir(current_dir)}")

    # List files in the parent directory
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    print(f"Parent directory: {parent_dir}")
    print(f"Files in parent directory: {os.listdir(parent_dir)}")

    # List files in the directory two levels up
    grandparent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
    print(f"Grandparent directory: {grandparent_dir}")
    print(f"Files in grandparent directory: {os.listdir(grandparent_dir)}")

    # Check if credentials file exists
    credentials_exists = os.path.isfile(credentials_path)
    print(f"Does credentials file exist? {credentials_exists}")

    # If the credentials file does not exist, try an alternative path
    if not credentials_exists:
        # Check if credentials are in /app/resources/credentials.json
        alternative_path = '/app/resources/credentials.json'
        if os.path.isfile(alternative_path):
            credentials_path = alternative_path
            print(f"Using alternative credentials path: {credentials_path}")
            logging.info(f"Using alternative credentials path: {credentials_path}")
        else:
            print(f"Alternative credentials path does not exist: {alternative_path}")
            logging.info(f"Alternative credentials path does not exist: {alternative_path}")

    append_to_google_sheet(box_scores, credentials_path)


if __name__ == '__main__':
    main()