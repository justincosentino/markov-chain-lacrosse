'''
'''


# ---------------------------------------------------------------------------- #


from __future__ import division
from schedule_class import Schedule
from team_class import Team
import numpy as np
import random
import matrices


# --------------------------------------------------------------------------- #
# SIMULATION


def generate_season_schedule(schedule):
	# Generate a list of games to play ordered by team name, date
	games_to_play = {}
	for team_name in schedule.get_teams():
		for game_info in schedule.get_full_schedule_results(team_name):
			date, opponent_name = game_info[1], game_info[3]
			team_score, opp_score = game_info[4], game_info[5]
			location = game_info[2]
			game = (date, team_name, opponent_name)
			unique_game = tuple(sorted(game))
			if unique_game not in games_to_play:
				games_to_play[game] = (team_score, opp_score, location)

	games_to_simulate = []			
	games_to_simulate = [g+games_to_play[g] for g in games_to_play]
	games_to_simulate = sorted(games_to_simulate, 
		key=lambda tup: (tup[1], tup[0]))	
	return games_to_simulate


def winning_probability(team_1, team_2, num_samples, scores, to_print=True):
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
	output_1 = 'Team: %s, Won: %3d, Lost: %3d, Tied: %3d, Total: %3d, Percent: %f' % (team_1, team_1_wins, team_2_wins, ties, num_samples, team_1_wins / num_samples)
	output_2 = 'Team: %s, Won: %3d, Lost: %3d, Tied: %3d, Total: %3d, Percent: %f' % (team_2, team_2_wins, team_1_wins, ties, num_samples, team_2_wins / num_samples)
	if to_print:
		print output_1
		print output_2
	if (team_1_wins / num_samples) > (team_2_wins / num_samples):
		return team_1.team_name
	else:
		return team_2.team_name


def get_ground_truth_winner(game):
	if game[3] > game[4]:
		return game[1]
	else: 
		return game[2]


def _single_game(team_1, team_2, team_1_exp_off_pos, team_2_exp_off_pos, 
	matrix, hfa):

	total_exp_pos = team_1_exp_off_pos + team_2_exp_off_pos

	# Determine which team will start with the ball based on fo stats
	adjusted_fo_perc = (team_1.fos_win_perc + (1-team_2.fos_win_perc)) / 2
	if random.random() < adjusted_fo_perc:
		state = np.array([1, 0, 0, 0, 0, 0])
	else:
		state = np.array([0, 1, 0, 0, 0, 0])
	
	# Since goals count as steps of the chain, add expected goals to 
	# expected possessions
	num_iterations = (total_exp_pos + team_1.goals_per_game + 
		team_2.goals_per_game)
	score = [0,0]

	# Account for HFA
	if hfa:
		score = [1,0]
	else:
		score = [0,1]


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
				if i == 4:
					score[0] += 1
				elif i == 5:
					score[1] +=1
				break
	
	return score


def _simulate_game(team_1, team_2, game, schedule, to_print=True):
	if to_print: print '#'

	# Determine expected number of offensive possessions for each team
	team_1_exp_off_pos = (team_1.fos_wins_per_game + 
				          team_1.num_clears_attempts_per_game +
				          team_2.num_clears_failed_per_game)
	team_2_exp_off_pos = (team_2.fos_wins_per_game + 
				          team_2.num_clears_attempts_per_game +
				          team_1.num_clears_failed_per_game)

	# Fetch transition matrix
	# matrix = matrices.team_avg(team_1, team_2,
	# 	team_1_exp_off_pos, team_2_exp_off_pos)
	# matrix = matrices.single_team(team_1,
	# 	team_1_exp_off_pos, team_2_exp_off_pos)
	matrix = matrices.sos(team_1, team_2, team_1_exp_off_pos, 
		team_2_exp_off_pos, schedule)

	# Include HFA
	hfa = False
	if game[5] == 'H': 
		hfa = True

	# Simulate games between the two teams
	num_samples = 250
	scores = []
	for sample in range(num_samples):
		scores.append(_single_game(team_1, team_2, team_1_exp_off_pos, \
			team_2_exp_off_pos, matrix, hfa))
	
	# Calculate winning probabilities and determine predicted winner
	winner = winning_probability(team_1, team_2, num_samples, scores)
	ground_truth_winner = get_ground_truth_winner(game)

	if winner == ground_truth_winner:
		if to_print: print 'Predicted: %s ' % winner
		return 1
	else: 
		if to_print: print 'Predicted: %s ' % winner
		return 0


def simulate_games(games_to_simulate, stats_db, schedule):
	
	num_played = 0
	num_correct = 0

	for game in games_to_simulate:

		date        = game[0]
		team_1_name = game[1]
		team_2_name = game[2]

		team_1 = Team(team_1_name, date, stats_db)
		team_2 = Team(team_2_name, date, stats_db)
		
		num_correct += _simulate_game(team_1, team_2, game, schedule)
		num_played += 1

 	print '#'
	print 'RESULTS: %d/%d=%f' % (num_correct, num_played, 
		num_correct / num_played)
	return


def _random_game(team_1_name, team_2_name, game):
	# Calculate winning probabilities and determine predicted winner
	winner = random.choice([team_1_name, team_2_name])
	ground_truth_winner = get_ground_truth_winner(game)

	output_1 = 'Team: %s' % (team_1_name)
	output_2 = 'Team: %s' % (team_2_name)
	print output_1
	print output_2

	if winner == ground_truth_winner:
		print 'Predicted: %s -- CORRECT' % winner
		return 1
	else: 
		print 'Predicted: %s -- INCORRECT' % winner
		return 0


def random_winner(games_to_simulate, stats_db):
	num_played = 0
	num_correct = 0

	for game in games_to_simulate:

		date        = game[0]
		team_1_name = game[1]
		team_2_name = game[2]

		num_correct += _random_game(team_1_name, team_2_name, game)
		num_played += 1

 	print '#'
	print 'RESULTS: %d/%d=%f' % (num_correct, num_played, 
		num_correct / num_played)
	return


def simulate_round_1(games_to_simulate, stats_db_path, schedule):

	for game in games_to_simulate:

		date        = game[0]
		team_1_name = game[1]
		team_2_name = game[2]

		team_1 = Team(team_1_name, date, stats_db_path)
		team_2 = Team(team_2_name, date, stats_db_path)
		
		_simulate_game(team_1, team_2, game, schedule)

	return


# --------------------------------------------------------------------------- #

def tournament():
	schedule_db_path = './../databases/ncaa_mlax_div_1_2015_sched.db'
	schedule = Schedule(schedule_db_path)

	stats_db_path = './../databases/ncaa_mlax_div_1_2015.db'

	games_to_simulate = [
			('2015-05-08', 'Notre Dame', 'Towson', 0, 0, 'H'),
			('2015-05-08', 'Albany (NY)', 'Cornell', 0, 0, 'A'),
			('2015-05-08', 'Duke', 'Ohio St.', 0, 0, 'H'),
			('2015-05-08', 'Brown', 'Denver', 0, 0, 'A'),
			('2015-05-08', 'Colgate', 'North Carolina', 0, 0, 'A'),
			('2015-05-08', 'Maryland', 'Yale', 0, 0, 'H'),
			('2015-05-08', 'Johns Hopkins', 'Virginia', 0, 0, 'A'),
			('2015-05-08', 'Marist', 'Syracuse', 0, 0, 'A'),
		]
	simulate_round_1(games_to_simulate, stats_db_path, schedule)
	return


def base_results():
	schedule_db_path = './../databases/ncaa_mlax_div_1_2014_sched.db'
	schedule = Schedule(schedule_db_path)

	stats_db_path = './../databases/ncaa_mlax_div_1_2014.db'

	games_to_simulate = generate_season_schedule(schedule)
	random_winner(games_to_simulate, stats_db_path)
	return


def main():
	schedule_db_path = './../databases/ncaa_mlax_div_1_2014_sched.db'
	schedule = Schedule(schedule_db_path)

	stats_db_path = './../databases/ncaa_mlax_div_1_2014.db'

	games_to_simulate = generate_season_schedule(schedule)
	simulate_games(games_to_simulate, stats_db_path, schedule)
	return


if __name__ == '__main__': 
	main()
	# base_results()
	# tournament()	


# --------------------------------------------------------------------------- #

