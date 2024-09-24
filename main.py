import requests
import os
import json
import time
# from heroes import get_hero_infos
from collections import Counter

cache_dir = "cache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

def get_cache_filename(name):
	return f"{cache_dir}/{name}.json"

def get_cache(name):
	path = get_cache_filename(name)
	if os.path.isfile(path):
		with open(path, "r") as f:
			return json.loads(f.read())
	return None

def save_cache(name, data):
	path = get_cache_filename(name)
	with open(path, "w+") as f:
		f.write(json.dumps(data, indent="\t"))

def do_web_request(url, cache_name=None):
	# print(cache_name)
	if cache_name:
		data = get_cache(cache_name)
		if data:
			return data
	response = requests.get(url)
	if response.status_code == 429:
		seconds_to_wait = 10
		print(f"being rate limited, waiting {seconds_to_wait} seconds...")
		time.sleep(seconds_to_wait)
		return do_web_request(url, cache_name)
	elif response.status_code != 200:
		print(response.headers)
		raise Exception(f"shit broke: {response.status_code}")
	data = response.json()
	if cache_name:
		save_cache(cache_name, data)
	return data

def create_hero_grid_config(categories):
	hero_grid = {
		"config_name": "Most Played",
		"categories": []
	}
	names = {
		"safe": "Safe Lane",
		"mid": "Mid Lane",
		"off": "Offlane",
		"support": "Support"
	}

	for category in categories:
		hero_counts = sorted(Counter(categories[category]).items(), key=lambda x: x[1], reverse=True)
		cat_info = {
			"category_name": names[category],
			"x_position": 0,
			"y_position": 0,
			"width": 0,
			"height": 0,
			"hero_ids": []
		}
		for hero_count in hero_counts:
			cat_info["hero_ids"].append(hero_count[0])
		hero_grid["categories"].append(cat_info)

	max_width = 1000
	max_height = 550
	gap = 0
	num_categories = len(hero_grid["categories"])
	category_height = (max_height / num_categories) - gap

	for i in range(0, num_categories):
		cat = hero_grid["categories"][i]
		cat["x_position"] = 0
		cat["y_position"] = (i * category_height) + (i * gap)
		cat["width"] = max_width
		cat["height"] = category_height

	return {
		"version": 3,
		"configs": [
			hero_grid
		]
	}


# prints the rankdiff for a single match
def singlematch_addhero(steamid, match_id, categories):
	match = do_web_request(f"http://api.opendota.com/api/matches/{match_id}", f"match_{match_id}")
	players = match["players"]
	radiant = list(filter(lambda p: p["player_slot"] < 128, players))
	dire = list(filter(lambda p: p["player_slot"] >= 128, players))

	player = None
	for p in players:
		if p["account_id"] == steamid:
			player = p

	if player is None:
		return #skip


	is_radiant = player["player_slot"] < 128

	team = radiant if is_radiant else dire

	lanes = {1: "safe", 2: "mid", 3: "off"}
	gold_key = "lane_efficiency"

	if "lane_role" not in player:
		return # skip this match as it hasnt been parsed

	hero_id = player["hero_id"]
	lane_role = player["lane_role"]
	team_lane = list(filter(lambda p: p["lane_role"] == lane_role, team))

	if any(p[gold_key] > player[gold_key] for p in team_lane):
		categories["support"].append(hero_id)
	else:
		if hero_id == 119:
			print(match_id)
		categories[lanes[lane_role]].append(hero_id)

def main(steamid, days, queryargs=None):
	url = f"http://api.opendota.com/api/players/{steamid}/matches?date={days}"
	matches_cache = f"matches_{days}"
	if queryargs:
		matches_cache += f"_{hash(queryargs)}"
		url += f"&{queryargs}"
	print(url)
	match_stubs = do_web_request(url)

	# player = do_web_request(f"http://api.opendota.com/api/players/{steamid}", f"player_{steamid}")
	
	matches = []
	for stub in match_stubs:
		match_id = stub["match_id"]
		matches.append(do_web_request(f"http://api.opendota.com/api/matches/{match_id}", f"match_{match_id}"))

	alldiffs = []

	matches.reverse()

	categories = {
		"safe": [],
		"mid": [],
		"off": [],
		"support": []
	}

	buffs = []

	for match in matches:
		print(match["match_id"])
		players = match["players"]
		for player in players:
			for buff in (player.get("permanent_buffs", []) or []):
				buff = buff["permanent_buff"]
				if buff not in buffs:
					buffs.append(buff)



	# with open("out.csv", "w+") as f:
	# 	f.write(csv_data)
	for buff in buffs:
		print(buff)

	# print(f"average: {avg(alldiffs):.2f}")


# all
# main(95211699, 60)

# ranked
# main(95211699, 60, "lobby_type=7")

# unranked
# main(95211699, 60, "lobby_type=0")

# with teammate
# main(95211699, 60, "included_account_id=170801607")

# ranked w/ teammate
main(95211699, 30)

# singlematch(95211699, 4997722586)

