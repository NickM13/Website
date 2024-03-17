import datetime

from .models import Summoner, ChampionMastery, MatchInfo, MatchMetadata, Match, MatchParticipant, MatchTeam
from .app import db
from .app import lol_watcher
import time


def get_summoner_by_name(summoner_name, region='NA1'):
	summoner = Summoner.query.filter(Summoner.name.ilike(f'{summoner_name}')).filter(Summoner.region.ilike(f'{region}')).first()
	data = lol_watcher.summoner.by_name(region, summoner_name)
	if summoner is None:
		summoner = Summoner(
			accountId=data['accountId'],
			profileIconId=data['profileIconId'],
			revisionDate=data['revisionDate'],
			name=data['name'],
			id=data['id'],
			puuid=data['puuid'],
			summonerLevel=data['summonerLevel'],
			region=region)
		db.session.add(summoner)
		db.session.commit()
	return summoner


def get_summoner_by_puuid(puuid, region='NA1'):
	summoner = Summoner.query.filter_by(puuid=puuid).first()
	data = lol_watcher.summoner.by_puuid(region, puuid)
	if summoner is None:
		summoner = Summoner(
			accountId=data['accountId'],
			profileIconId=data['profileIconId'],
			revisionDate=data['revisionDate'],
			name=data['name'],
			id=data['id'],
			puuid=data['puuid'],
			summonerLevel=data['summonerLevel'])
		db.session.add(summoner)
		db.session.commit()
	return summoner


def puuids_to_summoners(puuids):
	summoners = []
	for puuid in puuids:
		summoners.append(get_summoner_by_puuid(puuid))
	return summoners


def info_to_participants(info_list):
	participants = []
	for info in info_list:
		participants.append(MatchParticipant(
			assists=info['assists'],
			baronKills=info['baronKills'],
			bountyLevel=info['bountyLevel'],
			champExperience=info['champExperience'],
			champLevel=info['champLevel'],
			championId=info['championId'],
			championName=info['championName'],
			championTransform=info['championTransform'],
			consumablesPurchased=info['consumablesPurchased'],
			damageDealtToBuildings=info['damageDealtToBuildings'],
			damageDealtToObjectives=info['damageDealtToObjectives'],
			damageDealtToTurrets=info['damageDealtToTurrets'],
			damageSelfMitigated=info['damageSelfMitigated'],
			deaths=info['deaths'],
			detectorWardsPlaced=info['detectorWardsPlaced'],
			doubleKills=info['doubleKills'],
			dragonKills=info['dragonKills'],
			firstBloodAssist=info['firstBloodAssist'],
			firstBloodKill=info['firstBloodKill'],
			firstTowerAssist=info['firstTowerAssist'],
			firstTowerKill=info['firstTowerKill'],
			gameEndedInSurrender=info['gameEndedInSurrender'],
			goldEarned=info['goldEarned'],
			goldSpent=info['goldSpent'],
			individualPosition=info['individualPosition'],
			inhibitorKills=info['inhibitorKills'],
			inhibitorTakedowns=info['inhibitorTakedowns'],
			inhibitorsLost=info['inhibitorsLost'],
			item0=info['item0'],
			item1=info['item1'],
			item2=info['item2'],
			item3=info['item3'],
			item4=info['item4'],
			item5=info['item5'],
			item6=info['item6'],
			itemsPurchased=info['itemsPurchased'],
			killingSprees=info['killingSprees'],
			kills=info['kills'],
			lane=info['lane'],
			largestCriticalStrike=info['largestCriticalStrike'],
			largestKillingSpree=info['largestKillingSpree'],
			largestMultiKill=info['largestMultiKill'],
			longestTimeSpentLiving=info['longestTimeSpentLiving'],
			magicDamageDealt=info['magicDamageDealt'],
			magicDamageDealtToChampions=info['magicDamageDealtToChampions'],
			magicDamageTaken=info['magicDamageTaken'],
			neutralMinionsKilled=info['neutralMinionsKilled'],
			nexusKills=info['nexusKills'],
			nexusTakedowns=info['nexusTakedowns'],
			nexusLost=info['nexusLost'],
			objectivesStolen=info['objectivesStolen'],
			objectivesStolenAssists=info['objectivesStolenAssists'],
			participantId=info['participantId'],
			pentaKills=info['pentaKills'],
			# perks
			physicalDamageDealt=info['physicalDamageDealt'],
			physicalDamageDealtToChampions=info['physicalDamageDealtToChampions'],
			physicalDamageTaken=info['physicalDamageTaken'],
			profileIcon=info['profileIcon'],
			puuid=info['puuid'],
			quadraKills=info['quadraKills'],
			riotIdName=info['riotIdName'],
			riotIdTagline=info['riotIdTagline'],
			role=info['role'],
			sightWardsBoughtInGame=info['sightWardsBoughtInGame'],
			spell1Casts=info['spell1Casts'],
			spell2Casts=info['spell2Casts'],
			spell3Casts=info['spell3Casts'],
			spell4Casts=info['spell4Casts'],
			summoner1Casts=info['summoner1Casts'],
			summoner1Id=info['summoner1Id'],
			summoner2Casts=info['summoner2Casts'],
			summoner2Id=info['summoner2Id'],
			summonerId=info['summonerId'],
			summonerLevel=info['summonerLevel'],
			summonerName=info['summonerName'],
			teamEarlySurrendered=info['teamEarlySurrendered'],
			teamId=info['teamId'],
			teamPosition=info['teamPosition'],
			timeCCingOthers=info['timeCCingOthers'],
			timePlayed=info['timePlayed'],
			totalDamageDealt=info['totalDamageDealt'],
			totalDamageDealtToChampions=info['totalDamageDealtToChampions'],
			totalDamageShieldedOnTeammates=info['totalDamageShieldedOnTeammates'],
			totalDamageTaken=info['totalDamageTaken'],
			totalHeal=info['totalHeal'],
			totalHealsOnTeammates=info['totalHealsOnTeammates'],
			totalMinionsKilled=info['totalMinionsKilled'],
			totalTimeCCDealt=info['totalTimeCCDealt'],
			totalTimeSpentDead=info['totalTimeSpentDead'],
			totalUnitsHealed=info['totalUnitsHealed'],
			tripleKills=info['tripleKills'],
			trueDamageDealt=info['trueDamageDealt'],
			trueDamageDealtToChampions=info['trueDamageDealtToChampions'],
			trueDamageTaken=info['trueDamageTaken'],
			turretKills=info['turretKills'],
			turretTakedowns=info['turretTakedowns'],
			turretsLost=info['turretsLost'],
			unrealKills=info['unrealKills'],
			visionScore=info['visionScore'],
			visionWardsBoughtInGame=info['visionWardsBoughtInGame'],
			wardsKilled=info['wardsKilled'],
			wardsPlaced=info['wardsPlaced'],
			win=info['win']))
	return participants


def insert_match(match_id):
	start = time.time()
	match = Match.query.filter_by(matchId=match_id).first()
	if match is None:
		data = lol_watcher.match.by_id('americas', match_id)
		summoners = puuids_to_summoners(data['metadata']['participants'])
		match_metadata = MatchMetadata(
			dataVersion=data['metadata']['dataVersion'],
			matchId=data['metadata']['matchId'],
			participants=summoners)
		participants = info_to_participants(data['info']['participants'])
		match_info = MatchInfo(
			gameCreation=data['info']['gameCreation'],
			gameDuration=data['info']['gameDuration'],
			gameEndTimestamp=data['info']['gameEndTimestamp'],
			gameId=data['info']['gameId'],
			gameMode=data['info']['gameMode'],
			gameName=data['info']['gameName'],
			gameStartTimestamp=data['info']['gameStartTimestamp'],
			gameType=data['info']['gameType'],
			gameVersion=data['info']['gameVersion'],
			mapId=data['info']['mapId'],
			participants=participants,
			platformId=data['info']['platformId'],
			queueId=data['info']['queueId'],
			tournamentCode=data['info']['tournamentCode'], )
		match = Match(
			matchMetadata=match_metadata,
			matchInfo=match_info)
		db.session.add(match)
		db.session.commit()
		print(f"added: {time.time() - start}")
		start = time.time()
	return match


def get_latest_matches(summoner: Summoner, limit=10):
	subquery = Match.query\
		.join(MatchInfo, Match.gameId == MatchInfo.gameId)\
		.join(MatchParticipant, MatchInfo.gameId == MatchParticipant.gameId)\
		.add_columns(MatchParticipant.summonerName)\
		.filter_by(summonerName=summoner.name)\
		.order_by(MatchInfo.gameCreation.desc())\
		.limit(limit)\
		.subquery()
	return Match.query.join(subquery, Match.id == subquery.c.id).join(MatchInfo, MatchInfo.gameId == Match.gameId).order_by(MatchInfo.gameCreation.desc()).all()


def insert_matches(summoner: Summoner):
	match_ids = lol_watcher.match.matchlist_by_puuid('americas', summoner.puuid)
	matches = []
	for i in range(5):
		print("Inserting match: " + match_ids[i])
		matches.append(insert_match(match_ids[i]))
	# for id in match_ids:
	# matches.append(insert_match(id))
	return matches


def insert_champion_masteries(summoner: Summoner):
	one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(weeks=1)
	if ChampionMastery.query.filter(ChampionMastery.updated < one_week_ago, ChampionMastery.puuid == summoner.puuid).first() or not ChampionMastery.query.filter(ChampionMastery.puuid == summoner.puuid).first():
		for entry in ChampionMastery.query.filter(ChampionMastery.puuid == summoner.puuid).all():
			db.session.delete(entry)
		data = lol_watcher.champion_mastery.by_summoner(summoner.region, summoner.id)
		for champion in data:
			champion_mastery = ChampionMastery(
				puuid=champion['puuid'],
				championPointsUntilNextLevel=champion['championPointsUntilNextLevel'],
				chestGranted=champion['chestGranted'],
				championId=champion['championId'],
				lastPlayTime=champion['lastPlayTime'],
				championLevel=champion['championLevel'],
				summonerId=champion['summonerId'],
				championPoints=champion['championPoints'],
				championPointsSinceLastLevel=champion['championPointsSinceLastLevel'],
				tokensEarned=champion['tokensEarned'])
			db.session.add(champion_mastery)
		db.session.commit()
	return ChampionMastery.query.filter(ChampionMastery.summonerId == summoner.id).all()
