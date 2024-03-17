import requests

# insert your Riot API key here
RIOT_API_KEY = 'RGAPI-828f8f23-348e-40ee-b84e-8be50c56070f'


def get_match_data(match_id, region='americas'):
	url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	return None


def get_match_ids(puuid, region='americas'):
	url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?api_key={RIOT_API_KEY}"
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	return None


def get_match_data(match_id, region='americas'):
	url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	return None


def get_summoner_by_name(summoner_name, region='na1'):
	url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={RIOT_API_KEY}"
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	return None


def get_champion_masteries(summoner_id, region='na1'):
	url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}?api_key={RIOT_API_KEY}"
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	return None


def get_champion_masteries_top(summoner_id, region='na1', count=3):
	url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}/top?count={count}?api_key={RIOT_API_KEY} "
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	return None

