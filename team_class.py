'''
'''

# --------------------------------------------------------------------------- #


from __future__ import division
from collections import defaultdict
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


	def __init__(self, team_name, week, stat_db_path):
		'''
		'''
		# Init variables
		self.team_name = team_name
		self.week = week
		self.stat_db_path = stat_db_path
		self._stats = {}
		self.record = '?-?'
		self.power_ranking = 0

		self.read_stats()
		
		self.game_number = self.num_games - 1 	# 0 indexing
		# self.calculate_power_ranking()		

		
		pp = pprint.PrettyPrinter(indent=4)
		# pp.pprint(self.__dict__)

		return


	def __str__(self):
		'''
		'''
		return '%s (%s, Week %d)' % (self.team_name, self.record, self.week)
		# return '%s' % (self.team_name)

	def read_stats(self):
		# Read from db
		conn = sqlite3.connect(self.stat_db_path)
		db = conn.cursor()
		conn.text_factory = str

		for table in self.table_names:
			query = 'SELECT * FROM %s WHERE name=? AND rpt_weeks=?' % table
			db.execute(query, (self.team_name, self.week))
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


	def calculate_record_weight(self):
		pass


	def calculate_power_ranking(self, Schedule):
		# rpi = .25*(calculate_record_weight(self.team_name)) +
		# 	  .50*(calculate_record_weight)
		return

# --------------------------------------------------------------------------- #


class Schedule:

	def __init__(self, schedule_db_path):
		self.schedule_db_path = schedule_db_path
		self._fetch_schedule()

	def _fetch_schedule(self):
		# Read from db
		conn = sqlite3.connect(self.schedule_db_path)
		db = conn.cursor()
		conn.text_factory = str

		query = '''SELECT * 
		 		   FROM Schedule 
			   	'''
		
		db.execute(query)
		data = db.fetchall()

		conn.close()
		self.schedule = defaultdict(list)
		for game in data:
			self.schedule[game[0]].append(game)
		
		for team in self.schedule:
			self.schedule[team].sort(key=lambda tup: tup[6]) 

		return


	def get_schedule_results(self, team_name, up_to_game_no):
		return self.schedule[team_name][:up_to_game_no+1]


	def get_full_schedule_results(self, team_name):
		return self.schedule[team_name]


	def get_schedule(self, team_name, up_to_game_no):
		return [game[3] for game in self.schedule[team_name][:up_to_game_no+1]]


	def get_full_schedule(self, team_name):
		return [game[3] for game in self.schedule[team_name]]


# --------------------------------------------------------------------------- #


if __name__ == '__main__':
	schedule = Schedule('./ncaa_mlax_div_1_2014_sched.db')
	cuse = Team('Syracuse', 21, './ncaa_mlax_div_1_2014.db')


# --------------------------------------------------------------------------- #


