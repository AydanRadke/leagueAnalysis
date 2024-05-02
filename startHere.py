import pandas as pd
import requests
import bs4
# This gets the html of a webpage that has my most recent games in it.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

res = requests.get('https://www.op.gg/summoners/na/Electricpotato76-NA1', headers=headers, allow_redirects=False)
res.raise_for_status()
# print(res.text)
for resp in res.history:
    print(resp.status_code, resp.url)

# This changes the html into a readable enough string.
onlineThing = bs4.BeautifulSoup(res.text, 'html.parser')
onlineThing = onlineThing.prettify()

# We get to start the fun part!!! Since we have a string, we are going to
# Split the string up game by game, and collect the data we need to analyze
games = []
# Splits the long html string up game by game
while True:
    start_games_index = onlineThing.find('"participants"')
    end_games_index = onlineThing[start_games_index + 1:].find('"participants"')
    games.append(onlineThing[start_games_index:start_games_index + end_games_index])
    onlineThing = onlineThing[start_games_index + end_games_index:]
    print(start_games_index)
    print(end_games_index)
    if end_games_index == -1:
        break

print(games)
