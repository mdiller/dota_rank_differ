import requests
import os
import json

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

def do_web_request(url, cache_name):
	print(cache_name)
	data = get_cache(cache_name)
	if data:
		return data
	response = requests.get(url)
	if response.status_code != 200:
		raise Exception(f"shit broke: {response.status_code}")
	data = response.json()
	save_cache(cache_name, data)
	return data

def ranktostars(rank):
	if rank is None:
		return None
	stars = rank % 10
	medal = rank // 10
	return (medal * 7) + (stars - 1)

def avg(items):
	n = 0
	for item in items:
		n += item
	return n / len(items)

min_ranks = 3

def rankdiff(team1, team2):
	def getrank(player):
		return ranktostars(player.get("rank_tier"))
	team1 = map(getrank, team1)
	team2 = map(getrank, team2)
	team1 = list(filter(lambda i: i is not None, team1))
	team2 = list(filter(lambda i: i is not None, team2))
	if len(team1) < min_ranks or len(team2) < min_ranks:
		return None
	return avg(team1) - avg(team2)



def main(steamid, days):
	match_stubs = do_web_request(f"http://api.opendota.com/api/players/{steamid}/matches?date={days}", f"matches_{days}")

	# player = do_web_request(f"http://api.opendota.com/api/players/{steamid}", f"player_{steamid}")
	
	matches = []
	for stub in match_stubs:
		match_id = stub["match_id"]
		matches.append(do_web_request(f"http://api.opendota.com/api/matches/{match_id}", f"match_{match_id}"))

	alldiffs = []

	for match in matches:
		# find myself and what team im on
		# team differentiated by dire >= 128, radiant < 128 in player_slot
		players = match["players"]
		radiant = list(filter(lambda p: p["player_slot"] < 128, players))
		dire = list(filter(lambda p: p["player_slot"] >= 128, players))

		is_radiant = any(p["account_id"] == steamid for p in radiant)

		if is_radiant:
			team1 = radiant
			team2 = dire
		else:
			team1 = dire
			team2 = radiant

		diff = rankdiff(team1, team2)
		if diff is not None:
			print(f"{diff:.2f}")
			alldiffs.append(diff)


	print(f"average: {avg(alldiffs):.2f}")



main(95211699, 60)