# wr-checker

Prerequisites:
sudo apt install python3-pip
pip3 install srcomapi

In the URLs.txt file add each run that you wish to follow, each on their own line.


Using subcategories:
Subcategories are a bit complicated so you have to manually find the name of the subcategories (variables) that you wish to filter for. This can be done by going to {https://www.speedrun.com/api/v1/games/[game]/variables}, for example: {https://www.speedrun.com/api/v1/games/sm64/variables}.

There are two ids that you will need to track a subcategory; the subcategory name and the subcategory value.
Example:
Subcategory name: Platform
Subcategory value: N64

*Getting the subcategory name:
From the variables page on the first line the very first id you see should be your subcategory name.
Example:
{"data":[{"id":"e8m7em86","name":"Platform","category":null ...
"Platform" is the subcategory name that we are trying to follow, so we want its corresponding id which is e8m7em86.

*Getting the subcategory value:
From the variables page press Ctrl-F and find the subcategory that you wish to track.
Example: Ctrl-F the term "N64" on the sm64 variables page which will bring up {"9qj7z0oq":"N64","jq6540ol":"VC","5lmoxk01":"EMU"}. We want the corresponding value for "N64", so the subcategory value we are looking for is "9qj7z0oq".

Now that we have the subcategory name and subcategory value you can add them to the URL of the game you wish to track preceded by a #. It should be in the following format:
https://www.speedrun.com/[game_name]#[category]#[subcategory_name]#[subcategory_value]
Example: https://www.speedrun.com/sm64#120_Star#e8m7em86#9qj7z0oq.
This is interpreted as follows:
Game: Super Mario 64
Category: 120 Star
Subcategory name: Platform
Subcategory value: N64
