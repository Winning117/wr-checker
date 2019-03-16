import urllib.request
import json
import sys

number_of_places = 3
given_url = ["https://www.speedrun.com/oot#Any", "https://www.speedrun.com/sm64#120_Star#e8m7em86#5lmoxk01"]
show_time_ahead = True

class Game(object):
    name = None # ex: Super Mario 64
    name_id = None # ex: sm64
    category = None # ex: 120_Star
    subcategory_name = None # ex: The ID for "Platform"
    subcategory_value = None # ex: The ID for "N64"
    runners = []

    # Constructor
    def __init__(self, name, name_id, category, subcategory_name, subcategory_value, runners):
        self.name = name
        self.name_id = name_id
        self.category = category
        self.subcategory_name = subcategory_name
        self.subcategory_value = subcategory_value
        self.runners = runners


# when giving the URL the API says it prefers using the game ID
# get_json takes in the url found in a GET request, so after the ".com" portion of the URL
def get_json(game_info):
    j_obj = urllib.request.urlopen("https://www.speedrun.com/api/v1/leaderboards/" + game_info[0] + "/category/" + game_info[1] + "?top=" + str(number_of_places) + "&embed=players")
    return json.load(j_obj)


def convert_seconds_to_string(seconds):
    #time_list has hours, minutes, seconds, milliseconds
    time_list=[]
    # divmod converts seconds to hrs, min, sec
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time_list.append(h)
    time_list.append(m)
    time_list.append(s)

    time_string = ""
    # hours
    if (time_list[0] != 0):
        time_string += (str(time_list[0]) + "h ")
    # minutes
    if (time_list[1] != 0):
        time_string += (str(time_list[1]) + "m ")
    # seconds
    if (time_list[2] != 0):
        time_string += (str(time_list[2]) + "s")
    return time_string

# THIS ONLY WORKS WHEN GAMES DO NOT SPECIFY A SUB-CATEGORY
def get_top_players_list(json_object):
    top_players_list = []
    for x in range(0,number_of_places):
        run_info = []
        username = json_object["data"]["players"]["data"][x]["names"]["international"]
        run_info.append(username)

        time = json_object["data"]["runs"][x]["run"]["times"]["primary_t"]
        time_string = convert_seconds_to_string(time)
        run_info.append(time_string)
        top_players_list.append(run_info)
    return top_players_list


def get_info_from_json(url):
    game_info_list = get_game_info(url)
    json_object = get_json(game_info_list)
    top_players_list = get_top_players_list(json_object)
    return top_players_list


def convert_url_to_object(url):
    api_url = None
    game_name = None
    players = None
    game_info = url.split("https://www.speedrun.com/")[1].split("#")
    name_id = game_info[0]
    category = game_info[1]
    subcategory_name = None
    subcategory_value = None
    if len(game_info) == 4:
        subcategory_name = game_info[2]
        subcategory_value = game_info[3]
    if len(game_info) > 4:
        print("ERROR: Too many categories in the URL")
        sys.exit(1)

    if (subcategory_name == None) or (subcategory_value == None):
        api_url = "https://www.speedrun.com/api/v1/leaderboards/" + str(name_id) + "/category/" + str(category) + "?embed=players,game&top=" + str(number_of_places)
    else: # if we have a subcategory then make different API call
        api_url = "https://www.speedrun.com/api/v1/leaderboards/" + str(name_id) + "/category/" + str(category) + "?embed=players,game&top=" + str(number_of_places) + "&var-" + subcategory_name + "=" + subcategory_value

    print(api_url)
    json_obj = json.load(urllib.request.urlopen(api_url))

    game_name = json_obj["data"]["game"]["data"]["names"]["international"]
    players = get_top_players_list(json_obj)

    print(game_name, name_id, category, subcategory_name, subcategory_value, players)
    return Game(game_name, name_id, category, subcategory_name, subcategory_value, players)


def print_records(game):
    print(game.name)

def main():
    for x in given_url:
        game = convert_url_to_object(x)
        print_records(game)

if __name__ == "__main__":
    main()
