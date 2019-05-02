import urllib.request
import json
import sys
import configparser
from time import sleep
import subprocess
import datetime

number_of_players_to_track = None
show_time_behind_wr = None
show_date = None
show_days_ago = None
date_format = None
date_last_ran = None
urls = None


class Game(object):
    name = None  # ex: Super Mario 64
    name_id = None  # ex: sm64
    category = None  # ex: 120_Star
    variable_name = None  # ex: Platform
    variable_id = None  # ex: The ID for "Platform"
    choices_name = None  # ex: N64
    choices_id = None  # ex: The ID for "N64"
    runners = []

    # Constructor
    def __init__(self, name, name_id, category, variable_name, variable_id, choices_name, choices_id, runners):
        self.name = name
        self.name_id = name_id
        self.category = category
        self.variable_name = variable_name
        self.variable_id = variable_id
        self.choices_name = choices_name
        self.choices_id = choices_id
        self.runners = runners


# when giving the URL the API says it prefers using the game ID
# get_json takes in the url found in a GET request, so after the ".com" portion of the URL
def get_json(api_url):
    attempts = 0
    while attempts < 5:  # Retry if bad HTTP request
        try:
            j_obj = urllib.request.urlopen(api_url)
            break
        except:
            attempts += 1
            sleep(1)
    if attempts == 5:
        print("ERROR: Could not reach the server - the API might be down right now")
        sys.exit(1)
    return json.load(j_obj)


def convert_seconds_to_string(seconds):
    # time_list has hours, minutes, seconds, milliseconds
    time_list = []

    # divmod converts seconds to hrs, min, sec
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time_list.append(h)
    time_list.append(m)
    time_list.append(s)

    time_string = ""
    # hours
    if (time_list[0] != 0):
        time_string += str(str(int(time_list[0])) + "h ")
    # minutes
    if (time_list[1] != 0):
        time_string += str(str(int(time_list[1])) + "m ")
    # seconds
    if (time_list[2] != 0):
        time_as_float = None
        if isinstance(time_list[2], float):
            time_as_float = str('%.3f' % (time_list[2]))
            time_string += str(str(time_as_float) + "s")
        else:
            time_string += str(str(time_list[2]) + "s")
    return time_string


def get_days_ago(date_as_string):
    run_date = datetime.datetime.strptime(date_as_string, '%Y-%m-%d')
    today = datetime.datetime.today()
    days_ago = (today - run_date).days

    days_since_last_use = (today - date_last_ran).days

    if days_since_last_use >= days_ago:
        days_ago = str(days_ago) + "            NEW"

    return days_ago


def get_top_players_list(json_object):
    top_players_list = []
    wr_time = None
    for x in range(0, number_of_players_to_track):
        try:
            run_info = []
            time_behind_wr = None
            time_behind_wr_string = None
            username = None

            try:
                username = json_object["data"]["players"]["data"][x]["names"]["international"]
            except:
                # username is located in a different place if the user doesn't have an account
                username = json_object["data"]["players"]["data"][x]["name"]
                if "]" in username:
                    username = username.split(']')[1]
            run_info.append(username)

            time = json_object["data"]["runs"][x]["run"]["times"]["primary_t"]
            time_string = convert_seconds_to_string(time)
            run_info.append(time_string)

            if x == 0:
                wr_time = time
                time_behind_wr_string = ""
            else:
                time_behind_wr = time - wr_time
                time_behind_wr_string = "+" + convert_seconds_to_string(time_behind_wr)
            run_info.append(time_behind_wr_string)

            # get date from run
            date = json_object["data"]["runs"][x]["run"]["date"]
            days_ago = get_days_ago(date)
            date_list = date.split('-')
            year = date_list[0]
            month = date_list[1]
            day = date_list[2]
            if date_format.upper() == "MM/DD/YY":
                run_info.append(month + "/" + day + "/" + year)
            elif date_format.upper() == "DD/MM/YY":
                run_info.append(day + "/" + month + "/" + year)
            elif date_format.upper() == "YY/MM/DD":
                run_info.append(year + "/" + month + "/" + day)
            else:
                print("ERROR: Date specified is incorrect " + str(date))

            run_info.append(days_ago)

            top_players_list.append(run_info)
        except:
            pass
    return top_players_list


def get_variable_names_and_choice_names(json_object):
    variable_names = {}
    choice_names = {}
    variables_json_list = json_object["data"]["variables"]["data"]
    # for each variable name add to variable_names and choices_names
    for variable in range(0, len(variables_json_list)):
        variable_id = variables_json_list[variable]["id"]
        variable_name = variables_json_list[variable]["name"]
        variable_names[variable_id] = variable_name

        choice_list = variables_json_list[variable]["values"]["choices"]
        # add every choice to choice_names
        for choice in choice_list:
            choice_names[choice] = choice_list[choice]
    return variable_names, choice_names


def convert_url_to_object(url):
    api_url = None
    game_name = None
    players = None
    game_info = url.split("https://www.speedrun.com/")[1].split("#")
    name_id = None
    category = None
    variable_name = None
    variable_id = None
    choices_name = None
    choices_id = None

    if len(game_info) == 1:
        print("ERROR: You forgot to specify a category for " + url)
        sys.exit(1)
    name_id = game_info[0]
    category = game_info[1]

    if len(game_info) == 4:
        variable_id = game_info[2]
        choices_id = game_info[3]
    if len(game_info) > 4:
        print("ERROR: Too many categories in the URL")
        sys.exit(1)

    api_url = "https://www.speedrun.com/api/v1/leaderboards/" + str(name_id) + "/category/" + str(category) + "?embed=players,game,variables&top=" + str(number_of_players_to_track)
    if variable_id:
        api_url = api_url + "&var-" + variable_id + "=" + choices_id

    json_obj = get_json(api_url)

    if (variable_id != None):
        try:
            variable_names, choice_names = get_variable_names_and_choice_names(json_obj)
            variable_name = variable_names[variable_id]
            choices_name = choice_names[choices_id]
        except:
            print("ERROR: Invalid variable name " + str(variable_id) + ", make sure the variable in your URL is correct")
            sys.exit(1)
    # if variables exist but aren't specified then give a warning
    else:
        try:
            test = json_obj["data"]["variables"]["data"][0]["id"]
            print("\nWARNING: Variables exist for this category but were not specified")
        except:
            pass

    game_name = json_obj["data"]["game"]["data"]["names"]["international"]
    players = get_top_players_list(json_obj)
    return Game(game_name, name_id, category, variable_name, variable_id, choices_name, choices_id, players)


def print_records(game):
    border_line = "-------------------------------------------------------------------"
    header = '{0: <10} {1: <20} {2: <20} {3: <20} '.format("Place", "Username", "Time", "Time Behind WR")
    if show_date:
        border_line += "-----------------"
        header += '{0: <20} '.format("Date")
    if show_days_ago:
        border_line += "-------------------"
        header += '{0: <20} '.format("Days Ago")

    # print game header
    if game.variable_id == None:
        print("\n" + game.name + " - " + game.category)
    else:
        print("\n" + game.name + " - " + game.category + " - " + game.variable_name + ": " + game.choices_name)
    print(border_line)
    print(header)
    print(border_line)

    for x in range(0, len(game.runners)):
        record_string = '{0: <10} {1: <20} {2: <20} {3: <20} '.format(str(x+1), str(game.runners[x][0]), str(game.runners[x][1]), str(game.runners[x][2]))
        if show_date:
            record_string += '{0: <20} '.format(str(game.runners[x][3]))
        if show_days_ago:
            record_string += '{0: <20} '.format(str(game.runners[x][4]))
        print(record_string)
    print(border_line)


def read_config_file():
    global number_of_players_to_track
    global show_time_behind_wr
    global show_date
    global show_days_ago
    global date_format
    global date_last_ran
    global update_interval_in_minutes
    global notify_when_record_is_set
    global urls

    config = configparser.ConfigParser()
    config.read('config.ini')
    number_of_players_to_track = config.getint('SETTINGS', 'number_of_players_to_track')
    show_time_behind_wr = config.getboolean('SETTINGS', 'show_time_behind_wr')
    show_date = config.getboolean('SETTINGS', 'show_date')
    show_days_ago = config.getboolean('SETTINGS', 'show_days_ago')
    date_format = config.get('SETTINGS', 'date_format')
    date_last_ran = config.get('SETTINGS', 'date_last_ran')
    date_last_ran = datetime.datetime.strptime(date_last_ran, '%Y-%m-%d')
    urls = (config.get('SETTINGS', 'urls')).split(',')


def main():
    read_config_file()

    for x in urls:
        game = convert_url_to_object(x)
        print_records(game)

    # update the date_last_ran in the config file
    global date_last_ran
    today = str(datetime.datetime.today()).split(" ")[0]

    config = configparser.ConfigParser()
    config.read('config.ini')
    config['SETTINGS']['date_last_ran'] = str(today)  # create
    with open('config.ini', 'w') as configfile:    # save
        config.write(configfile)


if __name__ == "__main__":
    main()
