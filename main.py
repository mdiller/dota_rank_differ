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

def do_web_request(url, cache_name=None):
	# print(cache_name)
	if cache_name:
		data = get_cache(cache_name)
		if data:
			return data
	response = requests.get(url)
	if response.status_code != 200:
		raise Exception(f"shit broke: {response.status_code}")
	data = response.json()
	if cache_name:
		save_cache(cache_name, data)
	return data

def ranktostars(rank):
	if rank is None:
		return None
	stars = rank % 10
	medal = rank // 10
	return (medal * 7) + (stars - 1)

medal_strings = [ "Unranked", "Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine", "Immortal" ]

def avg(items):
	n = 0
	for item in items:
		n += item
	return n / len(items)

min_ranks = 3

# gets a rank string from its stars value
def rankstring(rank):
	medal = medal_strings[rank // 7]
	stars = (rank % 7) + 1
	return f"{medal} [{stars}]"

def rankdiff(team1, team2, printall=False):
	def getrank(player):
		return ranktostars(player.get("rank_tier"))
	team1 = map(getrank, team1)
	team2 = map(getrank, team2)
	team1 = list(filter(lambda i: i is not None, team1))
	team2 = list(filter(lambda i: i is not None, team2))
	if len(team1) < min_ranks or len(team2) < min_ranks:
		if printall:
			print(f"team1: {len(team1)} ranked players")
			print(f"team2: {len(team2)} ranked players")
		return None
	if printall:
		print("\nteam 1")
		for rank in team1:
			print(f"({rank}) {rankstring(rank)}")
		print(f"average:    ({avg(team1)}) {rankstring(int(avg(team1)))}")
		print("\nteam 2")
		for rank in team2:
			print(f"({rank}) {rankstring(rank)}")
		print(f"average:    ({avg(team2)}) {rankstring(int(avg(team2)))}")
	return avg(team1) - avg(team2)

# prints the rankdiff for a single match
def singlematch(steamid, match_id):
	match = do_web_request(f"http://api.opendota.com/api/matches/{match_id}", f"match_{match_id}")
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

	diff = rankdiff(team1, team2, True)
	if diff is None:
		print("not enough ranked players to show a diff")
		return
	print(f"diff: {diff:.2f}")

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

	csv_data = ""

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


# singlematch(95211699, 5004860090)