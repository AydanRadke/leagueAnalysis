"""This program webscrapes game data from a League of Legends website called op.gg. It downloads the webpage, parses
 the html, formats the data that we want, and then exports a dataframe as a csv file. I might change this file
 some time to add newer games into the dataframe, but collecting around the last 20 games will give a
 sufficient sample for the purposes of this project."""
import pandas as pd
import json
import requests
import bs4
# This gets the html of a webpage that has my most recent games in it.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

username = "Electricpotato76"
tag = "-NA1"
url = "https://www.op.gg/summoners/na/" + username + tag
webpage = requests.get(url, headers=headers, allow_redirects=False)
webpage.raise_for_status()

# This changes the html into a readable enough string.
webpage = bs4.BeautifulSoup(webpage.text, 'html.parser')
webpage = webpage.prettify()

# Split the string up game by game, and collect the data we need to analyze
games = []
# Splits the long html string up game by game
while True:
    start_games_index = webpage.find('"participants"')
    end_games_index = webpage[start_games_index + 1:].find('"participants"')

    # handles the exception to the last game on the page
    if end_games_index == -1:
        games.append(webpage[start_games_index:webpage.find('memo') + 1])
    else:
        games.append(webpage[start_games_index:start_games_index + end_games_index])

    webpage = webpage[start_games_index + end_games_index:]
    if end_games_index == -1:
        break


# Returns my team so that I can categorize by friendly and enemy stats
def find_team(game):
    user_index = game.find(username)
    team = game[user_index:]
    if team.find("RED") < team.find("BLUE"):
        return "RED"
    else:
        return "BLUE"


# This function is meant to take in either of the dictionaries we're dealing with, and get rid of the data we don't need
# and return what we do. Handles player data and game data
def format_data(data, team=None):
    # This is for the player data formatting:
    new_data = {}
    if isinstance(data, dict):
        # If we get a KeyError, we have a game with a different game mode than the normal one.
        # So, we have to handle this error.
        try:
            new_data["team_key"] = data["team_key"]
            new_data["position"] = data["position"]
        except KeyError:
            return None

        criteria = ['kill', 'death', 'assist', 'gold_earned', 'champion_level', 'total_damage_dealt',
                    'total_damage_dealt_to_champions', 'vision_score', 'minion_kill']
        for item in criteria:
            new_data[item] = data["stats"][item]
        new_data["laning_score"] = data["stats"]["op_score_timeline"][13]["score"]

    # This is for the team data formatting:
    else:
        criteria = ['is_win', 'gold_earned', 'rift_herald_kill', 'rift_herald_first',
                    'dragon_kill', 'dragon_first', 'baron_kill', 'baron_first', 'tower_kill', 'horde_kill']
        new_data['my_team'] = {}
        new_data['enemy_team'] = {}
        if team == data[0]['key']:
            for item in criteria:
                new_data['my_team'][item] = data[0]['game_stat'][item]
                new_data['enemy_team'][item] = data[1]['game_stat'][item]
        else:
            for item in criteria:
                new_data['my_team'][item] = data[1]['game_stat'][item]
                new_data['enemy_team'][item] = data[0]['game_stat'][item]
    return new_data


# This function finds the data for each team. The game is in JSON, so we use the json module to get teh data from it,
# and then format it using the format_data function
def find_game_stats(game, team):
    dictionary = game[game.find("teams") + 7:]
    dictionary = dictionary[:dictionary.find('],"') + 1]
    team_stats = json.loads(dictionary)
    team_stats = format_data(team_stats, team)
    return team_stats


# This function finds the data for each position in the game. Gets the json for each player, formats it, and then
# sorts it based on position
def find_player_stats(game, team):
    player_stats = {"my_top": None, "my_jungle": None, "my_mid": None, "my_adc": None, "my_support": None,
                    "enemy_top": None, "enemy_jungle": None, "enemy_mid": None, "enemy_adc": None, "enemy_support": None}
    for i in range(10):
        player = "{" + game[game.find('"team_key"'): game.find('}},"') + 2] + "}"
        player = json.loads(player)
        game = game[game.find('}},"') + 2:]
        player = format_data(player)
        # error handler for different game modes. Refer to format_data() function to see where this comes from.
        if player is None:
            return None

        # This statement sorts the data by comparing my team to the team of the player
        # and using certain values in the dictionary. Then, it deletes the final stuff we don't need
        if player["team_key"] == team:
            player_stats["my_" + player["position"].lower()] = player
            del player_stats["my_" + player["position"].lower()]["team_key"]
            del player_stats["my_" + player["position"].lower()]["position"]
        else:
            player_stats["enemy_" + player["position"].lower()] = player
            del player_stats["enemy_" + player["position"].lower()]["team_key"]
            del player_stats["enemy_" + player["position"].lower()]["position"]
    return player_stats


# This is the FUN part! We initialize an empty dataframe, then get the needed stats from each game and put that
# into a dataframe. After that, we concatenate into the dataframe named "df". Finally, we multiindex the
# dataframe, so that each game's data is separated!
df = pd.DataFrame()
for game in games:
    team = find_team(game)
    game_stats = find_game_stats(game, team)
    player_stats = find_player_stats(game, team)
# This handles the case of different game modes. Since the webscraper doesn't work for those, and they're irrelevant
    if game_stats is None or player_stats is None:
        continue
    temp_df = pd.DataFrame({**player_stats, **game_stats}).transpose()
    df = pd.concat([df, temp_df])

import numpy as np

df = df.reset_index().rename(columns={'index': 'role'})
df['game_id'] = np.floor(df.reset_index()['index']/12)
# reorder columns so game_id appears first
df = df[['game_id'] + [col for col in df.columns if col != 'game_id']]
df.to_csv('leaguedata.csv', index=False)
print(df.to_string())