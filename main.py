import urllib.request
import json
import sys

number_of_places = 3
given_url = "https://www.speedrun.com/oot#Any"
show_time_ahead = True


# returns a list [game, category]
def get_game_info(url):
    # strips the begining part of the url
    game_info = url.split("https://www.speedrun.com/")[1].split("#")
    return game_info

# when giving the URL the API says it prefers using the game ID
# get_json takes in the url found in a GET request, so after the ".com" portion of the URL
def get_json(game_info):
    j_obj = urllib.request.urlopen("https://www.speedrun.com/api/v1/leaderboards/" + game_info[0] + "/category/" + game_info[1] + "?top=" + str(number_of_places))
    return json.load(j_obj)

# returns the player's id given the json_object and position on the leaderboard
def get_player_id(json_object, position):
    return json_object["data"]["runs"][position]["run"]["players"][0]["id"]

def get_player_time(json_object, position):
    return json_object["data"]["runs"][position]["run"]["times"]["primary_t"]

def get_username(player_id):
    j_obj = urllib.request.urlopen("https://www.speedrun.com/api/v1/users/" + player_id)
    j = json.load(j_obj)
    return j["data"]["names"]["international"]

#TODO: CONVERT SECONDS TO APPROPRIATE TIMES, POSSIBLY USE DICTIONARY TO STORE h, s, ms, etc
def convert_seconds():

def get_first_place(url):
    game = get_game_info(url)
    json_object = get_json(game)
    player_id_list = []
    for x in range(0,number_of_places):
        mini_list = []
        id = get_player_id(json_object, x)
        id = get_username(id)
        mini_list.append(id)
        time = get_player_time(json_object, x)
        mini_list.append(time)
        player_id_list.append(mini_list)
    return player_id_list


print(get_first_place(given_url))
