'''
'''

# --------------------------------------------------------------------------- #


from __future__ import division
from collections import defaultdict
from datetime import datetime as dt
import sqlite3
import os


# --------------------------------------------------------------------------- #


class Schedule:

	def __init__(self, schedule_db_path):
		self.schedule_db_path = schedule_db_path
		self._fetch_schedule()

	def _fetch_schedule(self):
		if not os.path.isfile(self.schedule_db_path):
			print '%s: No such database exits. Exiting...' % (self.schedule_db_path)
			exit(1)


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
		self._schedule = defaultdict(list)
		self._results  = defaultdict(list)
		
		for game in data:
			self._schedule[game[0]].append(game)
		
		for team in self._schedule:
			self._schedule[team].sort(key=lambda tup: tup[6])

		return


	def get_teams(self):
		return sorted(self._schedule.keys())


	def get_schedule_results(self, team_name, through_date):
		games = []
		through_date = dt.strptime(through_date, '%Y-%m-%d')
		for game in self._schedule[team_name]:
			game_date = dt.strptime(game[1], '%Y-%m-%d')
			if game_date <= through_date:
				games.append(game)
		return games


	def get_full_schedule_results(self, team_name):
		return self._schedule[team_name]


	def get_schedule(self, team_name, through_date):
		games = []
		through_date = dt.strptime(through_date, '%Y-%m-%d')
		for game in self._schedule[team_name]:
			game_date = dt.strptime(game[1], '%Y-%m-%d')
			if game_date <= through_date:
				games.append(game[3])
		return games


	# def get_full_schedule(self, team_name):
	# 	return [game[3] for game in self._schedule[team_name]]


# --------------------------------------------------------------------------- #


if __name__ == '__main__':
	schedule = Schedule('./../databases/ncaa_mlax_div_1_2014_sched.db')


# --------------------------------------------------------------------------- #