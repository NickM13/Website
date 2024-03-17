from .app import db
import time
import datetime


class Summoner(db.Model):
	accountId = db.Column(db.String(56))
	profileIconId = db.Column(db.Integer, default=1)
	revisionDate = db.Column(db.BigInteger)
	name = db.Column(db.String(56))
	id = db.Column(db.String(63))
	puuid = db.Column(db.String(78), primary_key=True)
	summonerLevel = db.Column(db.BigInteger)
	region = db.Column(db.String(4), default="NA1")

	def __repr__(self):
		return f"Summoner('{self.id}', '{self.name}', '{self.summonerLevel}')"


class Match(db.Model):
	__tablename__ = 'match_data'

	id = db.Column(db.Integer, primary_key=True)
	matchId = db.Column(db.String(20), db.ForeignKey('match_metadata.matchId'))
	matchMetadata = db.relationship('MatchMetadata', backref='match_data', lazy=True)
	gameId = db.Column(db.Integer, db.ForeignKey('match_info.gameId'))
	matchInfo = db.relationship('MatchInfo', backref='match_data', lazy=True)

	def __repr__(self):
		return '<Match (metadata: %r, info: %r)>' % (self.matchMetadata, self.matchInfo)

	def get_participant(self, summoner):
		for participant in self.matchInfo.participants:
			if participant.puuid == summoner.puuid:
				return participant
		return None



metadata_participants = db.Table(
	'metadata_participants',
	db.Column('match_id', db.String(20), db.ForeignKey('match_metadata.matchId'), primary_key=True),
	db.Column('summoner_puuid', db.String(78), db.ForeignKey('summoner.puuid'), primary_key=True))


class MatchMetadata(db.Model):
	__tablename__ = 'match_metadata'

	dataVersion = db.Column(db.Integer)
	matchId = db.Column(db.String(20), primary_key=True)
	participants = db.relationship(
		'Summoner', secondary=metadata_participants, lazy='subquery',
		backref=db.backref('match_metadata', lazy=True))

	def __repr__(self):
		return '<MatchMetadata (dataVersion: %r, matchId: %r, participants: %r)>' % (self.dataVersion, self.matchId, self.participants)


info_participants = db.Table(
	'info_participants',
	db.Column('match_id', db.Integer, db.ForeignKey('match_info.gameId'), primary_key=True),
	db.Column('game_id', db.String(78), db.ForeignKey('match_participant.gameId'), primary_key=True))

info_teams = db.Table(
	'info_teams',
	db.Column('match_id', db.Integer, db.ForeignKey('match_info.gameId'), primary_key=True),
	db.Column('game_id', db.String(78), db.ForeignKey('match_team.gameId'), primary_key=True))

import math

class MatchInfo(db.Model):
	__tablename__ = 'match_info'

	gameCreation = db.Column(db.BigInteger)
	gameDuration = db.Column(db.BigInteger)
	gameEndTimestamp = db.Column(db.BigInteger)
	gameId = db.Column(db.Integer, primary_key=True)
	gameMode = db.Column(db.String)
	gameName = db.Column(db.String)
	gameStartTimestamp = db.Column(db.BigInteger)
	gameType = db.Column(db.String)
	gameVersion = db.Column(db.String)
	mapId = db.Column(db.String)
	participants = db.relationship('MatchParticipant', backref='match_info', lazy=True)
	platformId = db.Column(db.String)
	queueId = db.Column(db.Integer)
	teams = db.relationship('MatchTeam', backref='match_info', lazy=True)
	tournamentCode = db.Column(db.String)

	def get_game_creation(self):
		ago = time.time() - self.gameCreation / 1000
		if ago > 60:
			ago /= 60
			if ago > 60:
				ago /= 60
				type = "hour"
				an = True
			else:
				type = "minute"
				an = False
		else:
			type = "second"
			an = False
		ago = math.floor(ago)
		if ago > 1:
			out = f'{str(ago)} {type}s ago'
		else:
			if an:
				out = f'An {type} ago'
			else:
				out = f'A {type} ago'
		return out

	def get_game_duration(self):
		m, s = divmod(self.gameDuration, 60)
		return f'{m:02d}:{s:02d}'

	def get_game_mode(self):
		if self.queueId == 420:
			return "Ranked Solo"
		if self.queueId == 440:
			return "Ranked Flex"
		if self.queueId == 450:
			return "ARAM"
		return self.queueId

	def __repr__(self):
		return '<MatchInfo (gameId: %r, gameCreation: %r, gameType: %r, platformId: %r, queueId: %r)>' % (self.gameId, self.gameCreation, self.gameType, self.platformId, self.queueId)


class MatchParticipant(db.Model):
	__tablename__ = 'match_participant'

	id = db.Column(db.Integer, primary_key=True)
	gameId = db.Column(db.Integer, db.ForeignKey('match_info.gameId'), nullable=False)

	assists = db.Column(db.Integer)
	baronKills = db.Column(db.Integer)
	bountyLevel = db.Column(db.Integer)
	champExperience = db.Column(db.Integer)
	champLevel = db.Column(db.Integer)
	championId = db.Column(db.Integer)
	championName = db.Column(db.String)
	championTransform = db.Column(db.Integer)
	consumablesPurchased = db.Column(db.Integer)
	damageDealtToBuildings = db.Column(db.Integer)
	damageDealtToObjectives = db.Column(db.Integer)
	damageDealtToTurrets = db.Column(db.Integer)
	damageSelfMitigated = db.Column(db.Integer)
	deaths = db.Column(db.Integer)
	detectorWardsPlaced = db.Column(db.Integer)
	doubleKills = db.Column(db.Integer)
	dragonKills = db.Column(db.Integer)
	firstBloodAssist = db.Column(db.Boolean)
	firstBloodKill = db.Column(db.Boolean)
	firstTowerAssist = db.Column(db.Boolean)
	firstTowerKill = db.Column(db.Boolean)
	gameEndedInSurrender = db.Column(db.Boolean)
	goldEarned = db.Column(db.Integer)
	goldSpent = db.Column(db.Integer)
	individualPosition = db.Column(db.String)
	inhibitorKills = db.Column(db.Integer)
	inhibitorTakedowns = db.Column(db.Integer)
	inhibitorsLost = db.Column(db.Integer)
	item0 = db.Column(db.Integer)
	item1 = db.Column(db.Integer)
	item2 = db.Column(db.Integer)
	item3 = db.Column(db.Integer)
	item4 = db.Column(db.Integer)
	item5 = db.Column(db.Integer)
	item6 = db.Column(db.Integer)
	itemsPurchased = db.Column(db.Integer)
	killingSprees = db.Column(db.Integer)
	kills = db.Column(db.Integer)
	lane = db.Column(db.String)
	largestCriticalStrike = db.Column(db.Integer)
	largestKillingSpree = db.Column(db.Integer)
	largestMultiKill = db.Column(db.Integer)
	longestTimeSpentLiving = db.Column(db.Integer)
	magicDamageDealt = db.Column(db.Integer)
	magicDamageDealtToChampions = db.Column(db.Integer)
	magicDamageTaken = db.Column(db.Integer)
	neutralMinionsKilled = db.Column(db.Integer)
	nexusKills = db.Column(db.Integer)
	nexusTakedowns = db.Column(db.Integer)
	nexusLost = db.Column(db.Integer)
	objectivesStolen = db.Column(db.Integer)
	objectivesStolenAssists = db.Column(db.Integer)
	participantId = db.Column(db.Integer)
	pentaKills = db.Column(db.Integer)
	# perks
	physicalDamageDealt = db.Column(db.Integer)
	physicalDamageDealtToChampions = db.Column(db.Integer)
	physicalDamageTaken = db.Column(db.Integer)
	profileIcon = db.Column(db.Integer)
	puuid = db.Column(db.String(78))
	quadraKills = db.Column(db.Integer)
	riotIdName = db.Column(db.String)
	riotIdTagline = db.Column(db.String)
	role = db.Column(db.String)
	sightWardsBoughtInGame = db.Column(db.Integer)
	spell1Casts = db.Column(db.Integer)
	spell2Casts = db.Column(db.Integer)
	spell3Casts = db.Column(db.Integer)
	spell4Casts = db.Column(db.Integer)
	summoner1Casts = db.Column(db.Integer)
	summoner1Id = db.Column(db.Integer)
	summoner2Casts = db.Column(db.Integer)
	summoner2Id = db.Column(db.Integer)
	summonerId = db.Column(db.String)
	summonerLevel = db.Column(db.Integer)
	summonerName = db.Column(db.String)
	teamEarlySurrendered = db.Column(db.Boolean)
	teamId = db.Column(db.Integer)
	teamPosition = db.Column(db.String)
	timeCCingOthers = db.Column(db.Integer)
	timePlayed = db.Column(db.Integer)
	totalDamageDealt = db.Column(db.Integer)
	totalDamageDealtToChampions = db.Column(db.Integer)
	totalDamageShieldedOnTeammates = db.Column(db.Integer)
	totalDamageTaken = db.Column(db.Integer)
	totalHeal = db.Column(db.Integer)
	totalHealsOnTeammates = db.Column(db.Integer)
	totalMinionsKilled = db.Column(db.Integer)
	totalTimeCCDealt = db.Column(db.Integer)
	totalTimeSpentDead = db.Column(db.Integer)
	totalUnitsHealed = db.Column(db.Integer)
	tripleKills = db.Column(db.Integer)
	trueDamageDealt = db.Column(db.Integer)
	trueDamageDealtToChampions = db.Column(db.Integer)
	trueDamageTaken = db.Column(db.Integer)
	turretKills = db.Column(db.Integer)
	turretTakedowns = db.Column(db.Integer)
	turretsLost = db.Column(db.Integer)
	unrealKills = db.Column(db.Integer)
	visionScore = db.Column(db.Integer)
	visionWardsBoughtInGame = db.Column(db.Integer)
	wardsKilled = db.Column(db.Integer)
	wardsPlaced = db.Column(db.Integer)
	win = db.Column(db.Boolean)

	def get_kda_performance(self):
		if self.deaths == 0:
			return "great"
		kda = (self.kills + self.assists) / self.deaths
		if kda > 3:
			return "great"
		if kda > 2:
			return "good"
		return "normal"

	def get_kda(self):
		if self.deaths == 0:
			return "Perfect"
		kda = (self.kills + self.assists) / self.deaths
		return f'{kda:.2f}'

	def __repr__(self):
		return f"MatchParticipant('{self.puuid}', '{self.summonerName}')"


class MatchTeam(db.Model):
	__tablename__ = 'match_team'

	id = db.Column(db.Integer, primary_key=True)
	gameId = db.Column(db.Integer, db.ForeignKey('match_info.gameId'), nullable=False)

	# bans
	# objectives
	teamId = db.Column(db.Integer)
	win = db.Column(db.Boolean)


class ChampionMastery(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
	puuid = db.Column(db.String(78))
	championPointsUntilNextLevel = db.Column(db.BigInteger)
	chestGranted = db.Column(db.Boolean)
	championId = db.Column(db.BigInteger)
	lastPlayTime = db.Column(db.BigInteger)
	championLevel = db.Column(db.Integer)
	summonerId = db.Column(db.String)
	championPoints = db.Column(db.Integer)
	championPointsSinceLastLevel = db.Column(db.BigInteger)
	tokensEarned = db.Column(db.Integer)

	def __repr__(self):
		return f"ChampionMastery('{self.championPointsUntilNextLevel}', '{self.chestGranted}', '{self.championId}', '{self.lastPlayTime}', '{self.championLevel}'', '{self.summonerId}', '{self.championPoints}', '{self.championPointsSinceLastLevel}', '{self.tokensEarned})"
