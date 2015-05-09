'''
'''

# ---------------------------------------------------------------------------- #


import numpy as np


# ---------------------------------------------------------------------------- #


def check_normal(matrix):
	for i in matrix:
		total = 0
		for j in matrix:
			total += matrix[i][j]
		assert(total == 1.0)


# ---------------------------------------------------------------------------- #


def single_team(team, team_exp_off_pos, team_2_exp_off_pos):
	# States [1-O, 2-O, 1-UP, 2-UP, 1-G, 2-G]
	matrix = {}
	for i in range(6):
		matrix[i] = {}
		for j in range(6):
			matrix[i][j] = 0

	# Team 1 Off -> Team 1 Man Up (Expected number of man up attempts per pos)
	matrix[0][2] = (team.emo_attempts / team.num_games) / team_exp_off_pos
	# Team 1 Off -> Team 1 Goal (Avg of goals scored per pos and goals allowed per pos)
	matrix[0][4] = team.goals_per_game / team_exp_off_pos
	# Team 1 Off -> Team 2 Off
	matrix[0][1] = 1 - matrix[0][4] - matrix[0][2]

	# Team 2 Off -> Team 2 Man Up (Expected number of man up attempts per pos)
	matrix[1][3] = (team.mdd_opp_attempts / team.num_games) / team_2_exp_off_pos
	# Team 2 Off -> Team 2 Goal (Avg of goals scored per pos and goals allowed per pos)
	matrix[1][5] = team.goals_allowed_per_game / team_2_exp_off_pos
	# Team 2 Off -> Team 1 Off
	matrix[1][0] = 1 - matrix[1][3] - matrix[1][5]

	# Team 1 Man Up -> Team 1 Goal
	matrix[2][4] = team.emo_goal_perc
	# Team 1 Man Up -> Team 1 Off
	matrix[2][0] = (1 - matrix[2][4])/2
	# Team 1 Man Up -> Team 2 Off
	matrix[2][1] = (1 - matrix[2][4])/2

	# Team 2 Man Up -> Team 2 Goal
	matrix[3][5] = 1 - team.mdd_kill_perc
	# Team 2 Man Up -> Team 2 Off
	matrix[3][0] = (1 - matrix[3][5])/2
	# Team 2 Man Up -> Team 1 Off
	matrix[3][1] = (1 - matrix[3][5])/2

	# Team 1 Goal -> Team 1 Off
	matrix[4][0] = team.fos_win_perc
	# Team 1 Goal -> Team 2 Off
	matrix[4][1] = 1 - matrix[4][0]

	# Team 2 Goal -> Team 1 Off
	matrix[5][0] = team.fos_win_perc
	# Team 2 Goal -> Team 2 Off
	matrix[5][1] = 1 - matrix[5][0]

	# check_normal(matrix)
	matrix = np.array([[matrix[i][j] for j in sorted(matrix[i])] for i in sorted(matrix)])

	return matrix


# ---------------------------------------------------------------------------- #


def team_avg(team_1, team_2, team_1_exp_off_pos, team_2_exp_off_pos):
	# States [1-O, 2-O, 1-UP, 2-UP, 1-G, 2-G]

	matrix = {}
	for i in range(6):
		matrix[i] = {}
		for j in range(6):
			matrix[i][j] = 0

	# Team 1 Off -> Team 1 Man Up (Expected number of man up attempts per pos)
	matrix[0][2] = (team_2.mdd_opp_attempts / team_2.num_games) / team_1_exp_off_pos
	# Team 1 Off -> Team 1 Goal (Avg of goals scored per pos and goals allowed per pos)
	matrix[0][4] = ((team_1.goals_per_game + team_2.goals_allowed_per_game) / 2) / team_1_exp_off_pos
	# Team 1 Off -> Team 2 Off
	matrix[0][1] = 1 - matrix[0][4] - matrix[0][2]

	# Team 2 Off -> Team 2 Man Up (Expected number of man up attempts per pos)
	matrix[1][3] = (team_1.mdd_opp_attempts / team_1.num_games) / team_2_exp_off_pos
	# Team 2 Off -> Team 2 Goal (Avg of goals scored per pos and goals allowed per pos)
	matrix[1][5] = ((team_2.goals_per_game + team_1.goals_allowed_per_game) / 2) / team_2_exp_off_pos
	# Team 2 Off -> Team 1 Off
	matrix[1][0] = 1 - matrix[1][3] - matrix[1][5]

	# Team 1 Man Up -> Team 1 Goal
	matrix[2][4] = (team_1.emo_goal_perc + (1 - team_2.mdd_kill_perc)) / 2
	# Team 1 Man Up -> Team 1 Off
	matrix[2][0] = (1 - matrix[2][4])/2
	# Team 1 Man Up -> Team 2 Off
	matrix[2][1] = (1 - matrix[2][4])/2

	# Team 2 Man Up -> Team 2 Goal
	matrix[3][5] = (team_2.emo_goal_perc + (1 - team_1.mdd_kill_perc)) / 2
	# Team 2 Man Up -> Team 2 Off
	matrix[3][0] = (1 - matrix[3][5])/2
	# Team 2 Man Up -> Team 1 Off
	matrix[3][1] = (1 - matrix[3][5])/2

	# Team 1 Goal -> Team 1 Off
	matrix[4][0] = (team_1.fos_win_perc + (1-team_2.fos_win_perc)) / 2
	# Team 1 Goal -> Team 2 Off
	matrix[4][1] = 1 - matrix[4][0]

	# Team 2 Goal -> Team 1 Off
	matrix[5][0] = (team_1.fos_win_perc + (1-team_2.fos_win_perc)) / 2
	# Team 2 Goal -> Team 2 Off
	matrix[5][1] = 1 - matrix[5][0]

	# check_normal(matrix)
	matrix = np.array([[matrix[i][j] for j in sorted(matrix[i])] for i in sorted(matrix)])

	return matrix


# ---------------------------------------------------------------------------- #


def sos(team_1, team_2, team_1_exp_off_pos, team_2_exp_off_pos, schedule):
	# States [1-O, 2-O, 1-UP, 2-UP, 1-G, 2-G]

	matrix = {}
	for i in range(6):
		matrix[i] = {}
		for j in range(6):
			matrix[i][j] = 0

	# Factor in SOS
	team_1.calculate_strength_of_schedule(schedule)
	team_2.calculate_strength_of_schedule(schedule)
	rpi_difference = (team_1.rpi - team_2.rpi) / 1.5

	# print team_1, team_2, rpi_difference

	# Team 1 Off -> Team 1 Man Up (Expected number of man up attempts per pos)
	matrix[0][2] = (team_2.mdd_opp_attempts / team_2.num_games) / team_1_exp_off_pos
	# Team 1 Off -> Team 1 Goal (Avg of goals scored per pos and goals allowed per pos)
	matrix[0][4] = ((team_1.goals_per_game + team_2.goals_allowed_per_game) / 2) / team_1_exp_off_pos + rpi_difference
	# Team 1 Off -> Team 2 Off
	matrix[0][1] = 1 - matrix[0][4] - matrix[0][2]

	# Team 2 Off -> Team 2 Man Up (Expected number of man up attempts per pos)
	matrix[1][3] = (team_1.mdd_opp_attempts / team_1.num_games) / team_2_exp_off_pos
	# Team 2 Off -> Team 2 Goal (Avg of goals scored per pos and goals allowed per pos)
	matrix[1][5] = ((team_2.goals_per_game + team_1.goals_allowed_per_game) / 2) / team_2_exp_off_pos - rpi_difference
	# Team 2 Off -> Team 1 Off
	matrix[1][0] = 1 - matrix[1][3] - matrix[1][5]

	# Team 1 Man Up -> Team 1 Goal
	matrix[2][4] = (team_1.emo_goal_perc + (1 - team_2.mdd_kill_perc)) / 2 + rpi_difference
	# Team 1 Man Up -> Team 1 Off
	matrix[2][0] = (1 - matrix[2][4])/2
	# Team 1 Man Up -> Team 2 Off
	matrix[2][1] = (1 - matrix[2][4])/2

	# Team 2 Man Up -> Team 2 Goal
	matrix[3][5] = (team_2.emo_goal_perc + (1 - team_1.mdd_kill_perc)) / 2 - rpi_difference
	# Team 2 Man Up -> Team 2 Off
	matrix[3][0] = (1 - matrix[3][5])/2
	# Team 2 Man Up -> Team 1 Off
	matrix[3][1] = (1 - matrix[3][5])/2

	# Team 1 Goal -> Team 1 Off
	matrix[4][0] = (team_1.fos_win_perc + (1-team_2.fos_win_perc)) / 2 + rpi_difference
	# Team 1 Goal -> Team 2 Off
	matrix[4][1] = 1 - matrix[4][0]

	# Team 2 Goal -> Team 1 Off
	matrix[5][0] = (team_1.fos_win_perc + (1-team_2.fos_win_perc)) / 2 + rpi_difference
	# Team 2 Goal -> Team 2 Off
	matrix[5][1] = 1 - matrix[5][0]

	# check_normal(matrix)
	matrix = np.array([[matrix[i][j] for j in sorted(matrix[i])] for i in sorted(matrix)])

	for i in range(len(matrix)):
		if sum(matrix[i]) > 1:
			matrix[i] = matrix[i] / np.sum(matrix[i])
		assert(sum(matrix[i]) <= 1)

	return matrix


# ---------------------------------------------------------------------------- #

if __name__ == '__main__':
	from team_class import Team
	from schedule_class import Schedule

	schedule = Schedule('./../databases/ncaa_mlax_div_1_2014_sched.db')
	date = '2014-05-24'
	db = './../databases/ncaa_mlax_div_1_2014.db'

	team_1 = Team('Syracuse', date, db)
	team_2 = Team('Duke', date, db)

	team_1_exp_off_pos = (team_1.fos_wins_per_game + 
				          team_1.num_clears_attempts_per_game +
				          team_2.num_clears_failed_per_game)
	team_2_exp_off_pos = (team_2.fos_wins_per_game + 
				          team_2.num_clears_attempts_per_game +
				          team_1.num_clears_failed_per_game)

	print sos(team_1, team_2, team_1_exp_off_pos, team_2_exp_off_pos, schedule)


