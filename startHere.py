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

# Need to add functionality with the team variable in order to properly sort these data points
def find_game_stats(game):
    dictionary = game[game.find("teams") + 7: ]
    dictionary = dictionary[:dictionary.find('],"') + 1]
    print(dictionary)
    team_stats = json.loads(dictionary)
    return team_stats

def format_data(data):
    pass


# Need to add functionality with the team variable in order to properly sort these data points
def find_player_stats(game):
    player_stats = {"my_top": None, "my_jg": None, "my_mid": None, "my_adc": None, "my_sup": None,
                    "enemy_top": None, "enemy_jg": None, "enemy_mid": None, "enemy_adc": None, "enemy_sup": None,}
    for i in range(10):
        player = "{" + game[game.find('"team_key"'): game.find('}},"') + 2] + "}"
        player = json.loads(player)
        game = game[game.find('}},"') + 2:]
        print(player)
        #player = format_data(player)

# This is the main data collection loop, commented out for testing
#for game in games:
    #team = find_team(game)
    #print(team)
    #game_stats = find_game_stats(game)
    #player_stats = find_player_stats(game, team)
    #print(game)

# tests of individual functions
print(games[0])
find_player_stats(games[0])
find_game_stats(games[0])
