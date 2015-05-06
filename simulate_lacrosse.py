'''
'''


# ---------------------------------------------------------------------------- #

from __future__ import division
from team_class import Team
from team_class import Schedule
import random
import numpy as np

# ---------------------------------------------------------------------------- #
# UTILITIES

def check_normal(matrix):
	for i in matrix:
		total = 0
		for j in matrix:
			total += matrix[i][j]
		assert(total == 1.0)


def show_state(state, score, team_1, team_2):
	if state[0] == 1:
		print '%s has possession. (%d-%d)' % (team_1, score[0], score[1])
	elif state[1] == 1:
		print '%s has possession. (%d-%d)' % (team_2, score[0], score[1])
	elif state[2] == 1:
		print '%s is man-up. (%d-%d)' % (team_1, score[0], score[1])
	elif state[3] == 1:
		print '%s is man-up. (%d-%d)' % (team_2, score[0], score[1])
	elif state[4] == 1:
		print '%s scored! (%d-%d)' % (team_1, score[0], score[1])
	elif state[5] == 1:
		print '%s scored! (%d-%d)' % (team_2, score[0], score[1])
	

def winning_probability(team_1, team_2, num_samples, scores):
	'''
	'''
	# Determine number of wins and ties
	team_1_wins, team_2_wins, ties = 0, 0, 0
	for game in scores:
		if game[0] > game[1]:
			team_1_wins += 1
		elif game[1] > game[0]:
			team_2_wins += 1
		else:
			ties += 1

	# Build output strings
	output_1 = 'Team: %s, Won: %d, Lost: %d, Tied: %d, Total: %d, Percent: %f' % (team_1, team_1_wins, team_2_wins, ties, num_samples, team_1_wins / num_samples)
	output_2 = 'Team: %s, Won: %d, Lost: %d, Tied: %d, Total: %d, Percent: %f' % (team_2, team_2_wins, team_1_wins, ties, num_samples, team_2_wins / num_samples)
	print output_1
	print output_2
	return (team_1_wins / num_samples), (team_2_wins / num_samples)


def team_1_win(team_1_score, team_2_score):
	return team_1_score > team_2_score


def team_1_win_results(team_results, current_game):
	return team_results[current_game-1][4] > team_results[current_game-1][5]

# --------------------------------------------------------------------------- #
# SIMULATION


def generate_matrix_team(team_1, team_1_exp_off_pos, team_2_exp_off_pos):
	# States [1-O, 2-O, 1-UP, 2-UP, 1-G, 2-G]
	matrix = {}
	for i in range(6):
		matrix[i] = {}
		for j in range(6):
			matrix[i][j] = 0

	# Team 1 Off -> Team 1 Man Up (Expected number of man up attempts per pos)
	matrix[0][2] = (team_1.emo_attempts / team_1.num_games) / team_1_exp_off_pos
	# Team 1 Off -> Team 1 Goal (Avg of goals scored per pos and goals allowed per pos)
	matrix[0][4] = team_1.goals_per_game / team_1_exp_off_pos
	# Team 1 Off -> Team 2 Off
	matrix[0][1] = 1 - matrix[0][4] - matrix[0][2]

	# Team 2 Off -> Team 2 Man Up (Expected number of man up attempts per pos)
	matrix[1][3] = (team_1.mdd_opp_attempts / team_1.num_games) / team_2_exp_off_pos
	# Team 2 Off -> Team 2 Goal (Avg of goals scored per pos and goals allowed per pos)
	matrix[1][5] = team_1.goals_allowed_per_game / team_2_exp_off_pos
	# Team 2 Off -> Team 1 Off
	matrix[1][0] = 1 - matrix[1][3] - matrix[1][5]

	# Team 1 Man Up -> Team 1 Goal
	matrix[2][4] = team_1.emo_goal_perc
	# Team 1 Man Up -> Team 1 Off
	matrix[2][0] = (1 - matrix[2][4])/2
	# Team 1 Man Up -> Team 2 Off
	matrix[2][1] = (1 - matrix[2][4])/2

	# Team 2 Man Up -> Team 2 Goal
	matrix[3][5] = 1 - team_1.mdd_kill_perc
	# Team 2 Man Up -> Team 2 Off
	matrix[3][0] = (1 - matrix[3][5])/2
	# Team 2 Man Up -> Team 1 Off
	matrix[3][1] = (1 - matrix[3][5])/2

	# Team 1 Goal -> Team 1 Off
	matrix[4][0] = team_1.fos_win_perc
	# Team 1 Goal -> Team 2 Off
	matrix[4][1] = 1 - matrix[4][0]

	# Team 2 Goal -> Team 1 Off
	matrix[5][0] = team_1.fos_win_perc
	# Team 2 Goal -> Team 2 Off
	matrix[5][1] = 1 - matrix[5][0]

	# check_normal(matrix)

	return matrix

def generate_matrix_averages(team_1, team_2, team_1_exp_off_pos, team_2_exp_off_pos):
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

	return matrix


def simulate_game(team_1, team_2, to_print=False):
	'''
	'''
	# Determine expected number of offensive possessions for each team
	team_1_exp_off_pos = (team_1.fos_wins_per_game + 
				          team_1.num_clears_attempts_per_game +
				          team_2.num_clears_failed_per_game)

	team_2_exp_off_pos = (team_2.fos_wins_per_game + 
				          team_2.num_clears_attempts_per_game +
				          team_1.num_clears_failed_per_game)

	total_exp_pos  = team_1_exp_off_pos + team_2_exp_off_pos

	# Determine which team will start with the ball based on fo stats
	adjusted_fo_perc = (team_1.fos_win_perc + (1-team_2.fos_win_perc)) / 2
	r = random.random()

	if r < adjusted_fo_perc:
		state = [1, 0, 0, 0, 0, 0]
		possession = '%s' % team_1
	else:
		state = [0, 1, 0, 0, 0, 0]
		possession = '%s' % team_2

	# Generate transition matrix using team stats
	# matrix = generate_matrix_averages(team_1, team_2, team_1_exp_off_pos, team_2_exp_off_pos)
	matrix = generate_matrix_team(team_1, team_1_exp_off_pos, team_2_exp_off_pos)

	# Cast to numpy arrays
	state = np.array(state)
	matrix = np.array([[matrix[i][j] for j in sorted(matrix[i])] for i in sorted(matrix)])

	# Since goals count as steps of the chain, add expected goals to expected possessions
	num_iterations = total_exp_pos + team_1.goals_per_game + team_2.goals_per_game
	score = [0,0]
	man_ups = [0,0]
	possessions = [0,0]

	if to_print:
		print '\n# ------------------------------------------------------------- #'
		print '%s won the first face-off and has possession of the ball. (%d-%d)' % (possession, score[0], score[1])

	for step in range(int(num_iterations)):
		potential = np.dot(state,matrix)
		r =  random.random()
		for i, prob in enumerate(potential):
			
			# Update r value in order to find next state
			r = r - prob
			if r < 0:

				# Update State
				state = np.zeros(6)
				state[i] = 1

				# Update counts
				if i == 0: 		possessions[0] += 1
				elif i == 1:	possessions[1] += 1
				elif i == 2:	man_ups[0] += 1
				elif i == 3:	man_ups[1] += 1
				elif i == 4:	score[0] += 1
				elif i == 5:	score[1] +=1
				
				break

		if to_print:
			show_state(state, score, team_1, team_2)

	return (score, man_ups, possessions)


# --------------------------------------------------------------------------- #

def example_game_many(team_1_name, team_2_name):
	year = 2014
	db_path = './ncaa_mlax_div_1_2014.db'
	week = 21
	team_1 = Team(team_1_name, week, db_path)
	team_2 = Team(team_2_name, week, db_path)
	
	# Simulate games between the two teams
	num_samples = 500
	scores, man_ups, possessions = [], [], []
	for sample in range(num_samples):
		s, m, p = simulate_game(team_1, team_2, to_print=False)
		scores.append(s)
		man_ups.append(m)
		possessions.append(p)
	
	# stats(team_1, team_2, num_samples, scores, man_ups, possessions)
	team_1_perc, team_2_perc = winning_probability(team_1, team_2, num_samples, scores)
	hist_plot(team_1_name, team_2_name, scores)
	return

def example_game(team_1_name, team_2_name):
	year = 2014
	db_path = './ncaa_mlax_div_1_2014.db'
	week = 21
	team_1 = Team(team_1_name, week, db_path)
	team_2 = Team(team_2_name, week, db_path)
	s, m, p = simulate_game(team_1, team_2, to_print=True)
	print 'Final Score: %s: %d, %s: %d' % (team_1_name, s[0], team_2_name, s[1])
	return


def all_2014_results():
	year = 2014
	week_offset = 6

	schedule_db_path = './ncaa_mlax_div_1_2014_sched.db'
	schedule = Schedule(schedule_db_path)
	db_path = './ncaa_mlax_div_1_2014.db'

	total_games = 0
	total_correct = 0

	for team_1_name in schedule.schedule:

		# Get the give teams schedule
		team_schedule = schedule.get_full_schedule(team_1_name)
		team_results  = schedule.get_full_schedule_results(team_1_name)

		# Using 6...21 b/c its hard to reconcile weeks and game number 
		# and we are only simulating on 2014 (6...21 are reporting weeks)
		first_week = 6
		last_week = 21
		current_game = 1
		for week in range(first_week, last_week):

			# Update team to reflect current week
			try:
				team_1 = Team(team_1_name, week, db_path)
			except Exception:
				team_1 = Team(team_1_name, 21, db_path)

			# Play all the games in the reporting week
			while(current_game <= team_1.num_games):
				print '#'
				# Get the opponent team
				team_2_name = team_schedule[current_game-1]
				try:
					team_2 = Team(team_2_name, week, db_path)
				except Exception:
					team_2 = Team(team_2_name, 21, db_path)

				# Simulate games between the two teams
				num_samples = 500
				scores, man_ups, possessions = [], [], []
				for sample in range(num_samples):
					s, m, p = simulate_game(team_1, team_2, to_print=False)
					scores.append(s)
					man_ups.append(m)
					possessions.append(p)
				
				# stats(team_1, team_2, num_samples, scores, man_ups, possessions)
				team_1_perc, team_2_perc = winning_probability(team_1, team_2, num_samples, scores)
				if team_1_win(team_1_perc, team_2_perc) == team_1_win_results(team_results, current_game):
					print 'CORRECT'
					total_correct += 1
				else: 
					print 'INCORRECT'

				# Update the current game
				current_game += 1
				total_games += 1
	print '#'
	print 'RESULTS: %d/%d=%f' % (total_correct, total_games, total_correct / total_games)
	return


def main():
	# all_2014_results()
	# example_game('Duke', 'Syracuse')
	example_game_many('Duke', 'Syracuse')


# --------------------------------------------------------------------------- #


if __name__ == '__main__': 
	main()


# --------------------------------------------------------------------------- #