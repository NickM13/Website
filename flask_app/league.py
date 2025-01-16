from sqlalchemy.ext.hybrid import hybrid_property
from wtforms.fields.simple import BooleanField

from .app import db, riot_watcher
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateTimeField, DateField
from wtforms.validators import DataRequired
import time
import datetime
import math
from .app import lol_watcher
from .auth import User

league = Blueprint('league', __name__)


class RiotAccount(db.Model):
	puuid = db.Column(db.String(78), primary_key=True)
	gameName = db.Column(db.String(56))
	tagLine = db.Column(db.String(8))
	region = db.Column(db.String(16))


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
		return '<MatchMetadata (dataVersion: %r, matchId: %r, participants: %r)>' % (
			self.dataVersion, self.matchId, self.participants)


info_participants = db.Table(
	'info_participants',
	db.Column('match_id', db.Integer, db.ForeignKey('match_info.gameId'), primary_key=True),
	db.Column('game_id', db.String(78), db.ForeignKey('match_participant.gameId'), primary_key=True))

info_teams = db.Table(
	'info_teams',
	db.Column('match_id', db.Integer, db.ForeignKey('match_info.gameId'), primary_key=True),
	db.Column('game_id', db.String(78), db.ForeignKey('match_team.gameId'), primary_key=True))


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
		return '<MatchInfo (gameId: %r, gameCreation: %r, gameType: %r, platformId: %r, queueId: %r)>' % (
			self.gameId, self.gameCreation, self.gameType, self.platformId, self.queueId)


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
	riotIdGameName = db.Column(db.String)
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


def subregion_to_region(subregion):
	if subregion == "NA1" or subregion == "Americas":
		return "Americas"
	return "Americas"


def get_summoner_by_puuid(puuid, region='NA1'):
	riot_account = (RiotAccount.query
	                .filter(RiotAccount.puuid == puuid)
	                .filter(RiotAccount.region == region)
	                .first())
	if not riot_account:
		account = riot_watcher.account.by_puuid(subregion_to_region(region), puuid)
		riot_account = RiotAccount(
			puuid=account['puuid'],
			gameName=account['gameName'],
			tagLine=account['tagLine'],
			region=region
		)
		db.session.add(riot_account)
		db.session.commit()
	return get_summoner(riot_account)


def get_summoner_by_name_combine(riot_id, region='NA1'):
	name, tag = riot_id.split("#")
	return get_summoner_by_name(name, tag, region)


def get_summoner_by_name(game_name, tag_line, region='NA1'):
	riot_account = (RiotAccount.query
	                .filter(RiotAccount.gameName == game_name)
	                .filter(RiotAccount.tagLine == tag_line)
	                .filter(RiotAccount.region == region)
	                .first())
	if riot_account:
		return get_summoner(riot_account)

	account = riot_watcher.account.by_riot_id(subregion_to_region(region), game_name, tag_line)
	if not account:
		return None

	riot_account = (RiotAccount.query
	                .filter(RiotAccount.puuid == account['puuid'])
	                .filter(RiotAccount.region == region)
	                .first())
	if not riot_account:
		riot_account = RiotAccount(
			puuid=account['puuid'],
			gameName=account['gameName'],
			tagLine=account['tagLine'],
			region=region
		)
		db.session.add(riot_account)
		db.session.commit()

	return get_summoner(riot_account)


def get_summoner(account: RiotAccount):
	summoner = Summoner.query.filter(Summoner.puuid == account.puuid).first()
	if summoner is None:
		data = lol_watcher.summoner.by_puuid(account.region, account.puuid)
		summoner = Summoner(
			accountId=data['accountId'],
			profileIconId=data['profileIconId'],
			revisionDate=data['revisionDate'],
			name=data['name'],
			id=data['id'],
			puuid=data['puuid'],
			summonerLevel=data['summonerLevel'],
			region=account.region)
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
			riotIdGameName=info['riotIdGameName'],
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
		start = time.time()
	return match


def get_latest_matches(summoner: Summoner, limit=10):
	subquery = Match.query \
		.join(MatchInfo, Match.gameId == MatchInfo.gameId) \
		.join(MatchParticipant, MatchInfo.gameId == MatchParticipant.gameId) \
		.add_columns(MatchParticipant.summonerName) \
		.filter_by(summonerName=summoner.name) \
		.order_by(MatchInfo.gameCreation.desc()) \
		.limit(limit) \
		.subquery()
	return Match.query.join(subquery, Match.id == subquery.c.id).join(MatchInfo,
	                                                                  MatchInfo.gameId == Match.gameId).order_by(
		MatchInfo.gameCreation.desc()).all()


def insert_matches(summoner: Summoner, pages: int = 5, subregion: str = 'NA1'):
	matches = []
	page_size = 20
	for p in range(pages):
		match_ids = lol_watcher.match.matchlist_by_puuid(subregion_to_region(subregion), summoner.puuid, start=p * page_size)
		for i in range(page_size):
			matches.append(insert_match(match_ids[i]))
	return matches


def insert_champion_masteries(summoner: Summoner):
	one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(weeks=1)
	if ChampionMastery.query.filter(ChampionMastery.updated < one_week_ago,
	                                ChampionMastery.puuid == summoner.puuid).first() or not ChampionMastery.query.filter(
			ChampionMastery.puuid == summoner.puuid).first():
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


@league.route('/')
def home():
	return render_template('league_home.html')


@league.route('/match/add', methods=['GET', 'POST'])
def league_match_add():
	if request.method == 'POST':
		match_id = request.form.get('match_id')
		if match_id:
			insert_match(match_id)
			return "Match with ID {} has been inserted.".format(match_id)

	return render_template('match_add.html')


@league.route('/showall')
def show_all():
	return render_template('show_all.html', matches=Match.query.all())


@league.route('/history/<string:name>/<string:tagline>')
def history(name, tagline):
	summoner = get_summoner_by_name(name, tagline)
	# matches = insert_matches(summoner)
	matches = get_latest_matches(summoner, 100)
	return render_template('match_history.html', summoner=summoner, matches=matches)


@league.route('/summoner/update', methods=['POST'])
def summoner_update():
	summoner_puuid = request.args.get("summoner_puuid")
	region = request.args.get("region", "NA1")
	summoner = get_summoner_by_puuid(summoner_puuid, region)
	if not summoner:
		flash("Summoner not found!")
		return jsonify({"message": "Summoner not found"})
	insert_matches(summoner, 100)
	return jsonify({"message": str(summoner)})


@league.route('/all/winrates')
def all_winrates():
	users = User.query.filter(User.riot_id is not None).all()
	summoners = [get_summoner_by_name_combine(u.riot_id) for u in users]
	return render_template('league_winrates.html', summoners=summoners)


@league.route('/all/history')
def all_history():
	matches = Match.query.all()
	return render_template('match_history.html', summoner=summoner, matches=matches)


@league.route('/match_info', methods=['GET', 'POST'])
def match_info():
	match_id = request.args.get('match_id')

	if match_id is not None:
		match_data = lol_watcher.match.by_id(match_id)
		print(match_data)
		return render_template('match_info.html', match_data=match_data)

	return render_template('match_info.html')


@league.route('/champion/scouter', methods=['GET', 'POST'])
def champ_scouter():
	region = request.args.get('region')
	summoner_name = request.args.get('summoner')

	if region and summoner_name:
		summoner = get_summoner_by_name(summoner_name, region)

		if summoner:
			champions = insert_champion_masteries(summoner)
			return render_template('champion_scouter.html', summoner=summoner, champions=champions)

	return render_template('champion_scouter.html')
