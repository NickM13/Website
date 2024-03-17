from riotwatcher import LolWatcher
import json

lol_watcher = LolWatcher('RGAPI-828f8f23-348e-40ee-b84e-8be50c56070f')

my_region = 'na1'

me = lol_watcher.summoner.by_name(my_region, 'TheNickMead')
print(me)

# all objects are returned (by default) as a dict
# lets see if i got diamond yet (i probably didnt)
my_ranked_stats = lol_watcher.league.by_summoner(my_region, me['id'])
#print(my_ranked_stats)

match_ids = lol_watcher.match.matchlist_by_puuid('americas', me['puuid'])
print(match_ids)

match = lol_watcher.match.by_id('americas', match_ids[0])
print(match['info'])

# First we get the latest version of the game from data dragon
versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']

# Lets get some champions
current_champ_list = lol_watcher.data_dragon.champions(champions_version)
#print(current_champ_list)

# For Riot's API, the 404 status code indicates that the requested data wasn't found and
# should be expected to occur in normal operation, as in the case of a an
# invalid summoner name, match ID, etc.
#
# The 429 status code indicates that the user has sent too many requests
# in a given amount of time ("rate limiting").
