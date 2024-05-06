# import pandas as pd
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

# We get to start the fun part!!! Since we have a string, we are going to
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
def format_data(data):
    # This is for the player data formatting:
    new_data = {}
    if isinstance(data, dict):
        new_data["team_key"] = data["team_key"]
        new_data["position"] = data["position"]
        criteria = ['kill', 'death', 'assist', 'gold_earned', 'champion_level', 'total_damage_dealt',
                    'total_damage_dealt_to_champions', 'vision_score', 'minion_kill']
        for item in criteria:
            new_data[item] = data["stats"][item]
        new_data["laning_score"] = data["stats"]["op_score_timeline"][13]["score"]
        return new_data
    # This is for the team data formatting:
    # DO THIS NEXT! NEED TO COLLECT THE NEEDED GAME DATA POINTS, AND CONTINUE
    else:
        pass


# Need to add functionality with the team variable in order to properly sort these data points
def find_game_stats(game, team):
    dictionary = game[game.find("teams") + 7: ]
    dictionary = dictionary[:dictionary.find('],"') + 1]
    team_stats = json.loads(dictionary)
    #team_stats = format_data(team_stats)
    print(team_stats)
    return team_stats


# Need to add functionality with the team variable in order to properly sort these data points
def find_player_stats(game, team):
    player_stats = {"my_top": None, "my_jungle": None, "my_mid": None, "my_adc": None, "my_support": None,
                    "enemy_top": None, "enemy_jungle": None, "enemy_mid": None, "enemy_adc": None, "enemy_support": None,}
    for i in range(10):
        player = "{" + game[game.find('"team_key"'): game.find('}},"') + 2] + "}"
        player = json.loads(player)
        game = game[game.find('}},"') + 2:]
        player = format_data(player)
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
    for stat in player_stats:
        print(player_stats[stat])


# This is the main data collection loop, commented out for testing
#for game in games:
    #team = find_team(game)
    #print(team)
    #game_stats = find_game_stats(game, team)
    #player_stats = find_player_stats(game, team)
    #print(game)

# tests of individual functions
#print(games[0])
#find_player_stats(games[0], "RED")
find_game_stats(games[0], "RED")
