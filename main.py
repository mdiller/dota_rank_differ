import requests
import os
import json

def get_cache_filename(name):
	return f"cache/{name}.json"

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
	items = 
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

	for match in matches:
		# find myself and what team im on
		# team differentiated by dire >= 128, radiant < 128 in player_slot
				




main(95211699, 30)