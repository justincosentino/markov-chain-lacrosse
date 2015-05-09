
'''
'''

# --------------------------------------------------------------------------- #


from __future__ import division
from collections import defaultdict
from schedule_class import Schedule
import sqlite3
import pprint


# --------------------------------------------------------------------------- #


class Team:

	table_names = [	
			'assists_per_game',
			'ctos_per_game',
			'clearing_perc',
			'face_off_perc',
			'gbs_per_game',
			'mdd',
			'muo',
			'points_per_game',
			'saves_per_game',
			'scoring_defense',
			'scoring_margin',
			'scoring_offense',
			'shot_perc',
			'tos_per_game',
			'winning_perc'
		]


	def __init__(self, team_name, through_date, stat_db_path):
		'''
		'''
		# Init variables
		self.team_name = team_name
		self.through_date = through_date
		self.stat_db_path = stat_db_path
		self._stats = {}
		self.record = '?-?'
		self.rpi = 0

		self.read_stats()
		
		pp = pprint.PrettyPrinter(indent=4)
		# pp.pprint(self.__dict__)

		return


	def __str__(self):
		'''
		'''
		return '%16s (%s, %s)' % (self.team_name, self.record, self.through_date)
		return '%s' % (self.team_name)

	def read_stats(self):
		# Read from db
		conn = sqlite3.connect(self.stat_db_path)
		db = conn.cursor()
		conn.text_factory = str

		for table in self.table_names:
			query = 'SELECT * FROM %s WHERE name=? AND through_date<=? ORDER BY through_date DESC' % table
			db.execute(query, (self.team_name, self.through_date))
			rows = db.fetchone()
			
			# First few weeks are reported, so we just grab the first
			if not rows:
				query = 'SELECT * FROM %s WHERE name=? ORDER BY through_date ASC' % table
				db.execute(query, (self.team_name,))
				rows = db.fetchone()

			self._stats[table] = rows
			if table == 'winning_perc':
				self.record = '%d-%d' % (rows[2], rows[3])
		
		conn.close()
		self.update_internal_stats()
		return

	def update_internal_stats(self):
		# Update internal values
		self.num_wins  = self._stats['winning_perc'][2]
		self.num_loses = self._stats['winning_perc'][3]
		self.num_games = self.num_wins + self.num_loses
		self.win_perc  = self.num_wins / self.num_games

		self.num_goals = self._stats['scoring_offense'][4]
		self.goals_per_game = self.num_goals / self.num_games

		self.num_goals_allowed = self._stats['scoring_defense'][4]
		self.goals_allowed_per_game = self.num_goals_allowed / self.num_games

		self.num_fos_won  = self._stats['face_off_perc'][4]
		self.num_fos_lost = self._stats['face_off_perc'][5]
		self.num_fos = self.num_fos_won + self.num_fos_lost
		self.fos_win_perc = self.num_fos_won / self.num_fos
		self.fos_wins_per_game = self.num_fos_won / self.num_games

		self.emo_goals = self._stats['muo'][4]
		self.emo_attempts = self._stats['muo'][5]
		self.emo_goal_perc = self.emo_goals / self.emo_attempts
		self.emo_per_game = self.emo_attempts / self.num_games

		self.mdd_goals_against = self._stats['mdd'][4]
		self.mdd_opp_attempts  = self._stats['mdd'][5]
		self.mdd_kill_perc = 1 - self.mdd_goals_against / self.mdd_opp_attempts 

		self.scoring_margin = self._stats['scoring_margin'][6]

		self.num_assists = self._stats['assists_per_game'][4]
		self.assists_per_game = self.num_assists / self.num_games

		self.num_gbs = self._stats['gbs_per_game'][4]
		self.gbs_per_game = self.num_gbs / self.num_games

		self.num_shots = self._stats['shot_perc'][5]
		self.shot_perc = self.num_goals / self.num_shots

		self.num_saves = self._stats['saves_per_game'][4]
		self.saves_per_game = self.num_saves / self.num_games

		self.num_tos = self._stats['tos_per_game'][4]
		self.tos_per_game = self.num_tos / self.num_games

		self.num_clears_success  = self._stats['clearing_perc'][4]
		self.num_clears_attempts = self._stats['clearing_perc'][5]
		self.clear_perc = self.num_clears_success / self.num_clears_attempts
		self.num_clears_attempts_per_game = self.num_clears_attempts / self.num_games
		self.num_clears_failed_per_game = (self.num_clears_attempts - self.num_clears_success) / self.num_games

		self.num_points = self.num_goals + self.num_assists
		self.points_per_game = self.num_points / self.num_games

		self.num_ctos = self._stats['ctos_per_game'][4]
		self.ctos_per_game = self.num_ctos / self.num_games
		
		self._stats = None
		
		return


	def calculate_record_weight_opps_opps(self, opp_team_names, schedule):
		if len(opp_team_names) < 3:
			return .5
		win_percs = []
		for opp_team_name in opp_team_names:
			opp_opponents = schedule.get_schedule(opp_team_name, self.through_date)
			opp_opp_avg = self.calculate_record_weight_opps(opp_opponents, schedule)
			win_percs.append(opp_opp_avg)
		avg = sum(win_percs) / len(win_percs)
		return avg


	def calculate_record_weight_opps(self, opp_team_names, schedule):
		if len(opp_team_names) < 3:
			return .5
		win_percs = []
		for opp_team_name in opp_team_names:
			team = Team(opp_team_name, self.through_date, self.stat_db_path)
			win_percs.append(team.win_perc)
		avg = sum(win_percs) / len(win_percs)
		return avg


	def calculate_strength_of_schedule(self, schedule):
		opponents = schedule.get_schedule(self.team_name, self.through_date)
		curr_opponent = opponents[-1]
		past_opponents = opponents[:-1]
		rpi = (.25*self.win_perc + 
			   .50*self.calculate_record_weight_opps(past_opponents, schedule) +
			   .25*self.calculate_record_weight_opps_opps(past_opponents, schedule))
		self.rpi = rpi
		return


# --------------------------------------------------------------------------- #


if __name__ == '__main__':
	schedule = Schedule('./../databases/ncaa_mlax_div_1_2014_sched.db')
	date = '2014-05-24'
	db = './../databases/ncaa_mlax_div_1_2014.db'

	ratings = []
	for team_name in schedule.get_teams():
		team = Team(team_name, date, db)
		rating = team.calculate_strength_of_schedule(schedule)
		ratings.append((team_name, rating))
	ratings = sorted(ratings, key=lambda tup: tup[1])[::-1]
	for rating in ratings:
		print '%16s %f' % (rating[0], rating[1])


# --------------------------------------------------------------------------- #


