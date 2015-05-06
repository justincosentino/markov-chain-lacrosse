'''
'''


# --------------------------------------------------------------------------- #


from collections import defaultdict
import requests
import sqlite3
import sys
import re
import os
import pprint


# --------------------------------------------------------------------------- #


_BASE_URL = 'http://web1.ncaa.org/stats/StatsSrv/rankings'

_stat_map = {
	'assists_per_game':535,
	'ctos_per_game':561,
	'clearing_perc':838,
	'face_off_perc':230,
	'gbs_per_game':538,
	'mdd':232,
	'muo':231,
	'points_per_game':537,
	'saves_per_game':536,
	'scoring_defense':229,
	'scoring_margin':238,
	'scoring_offense':228,
	'shot_perc':563,
	'tos_per_game':559,
	'winning_perc':233
}


# --------------------------------------------------------------------------- #


def _isfloat(x):
	'''
	'''
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True


def _isint(x):
	'''
	'''
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


# --------------------------------------------------------------------------- #


def createTables(db, stats):
  	'''
  	'''
  	transactions = []

  	for stat in stats:
		columns = stats[stat][stats[stat].keys()[0]]['columns']
		example_team = stats[stat][stats[stat].keys()[0]]['Duke']

  		# Create table string
  		create_string = 'CREATE TABLE %s' % stat 
		
		# Create data type string
		type_string = ''
		for i in range(len(columns)):
			datatype = 'TEXT'
			if _isint(example_team[i]):
				datatype = 'INTEGER'
			elif _isfloat(example_team[i]):
				datatype = 'REAL'
			if columns[i].lower() == "to":
				columns[i] = "turnovers"
			type_string += '%s %s, ' % ('_'.join(re.findall(r"[\w']+", 
				columns[i].lower())), datatype)
		type_string += '%s %s, ' % ('rpt_weeks', 'INTEGER')
		
		# Create primary key string
		primary_key_string = 'PRIMARY KEY (name, rpt_weeks)'
		
		# Create total schema string
		schema_string = '%s (%s%s);' % (create_string, type_string, 
			primary_key_string)
		
		# Append all transactions to single list
		transactions.append(schema_string)

	# Execute all transactions
  	transaction_string = ' '.join(transactions)
  	try:
  		db.executescript(transaction_string)
  	except sqlite3.Error as e:
  		print 'An error occurred:', e.args[0]
  		print 'Deleting database and exiting...'
  		# TODO: Delete file
  		exit(1)

  	return


# --------------------------------------------------------------------------- #


def stats_generator(stats_stat, week):
	'''
	'''
	for team in stats_stat[week]:
		row = stats_stat[week][team]
		values = '"' + '","'.join(row) + '", "%s"' % (week)
		yield (values)

def insertAll(db, stats):
	'''
	'''
	for stat in stats:
		for week in stats[stat]:
			for team in stats[stat][week]:
				row = stats[stat][week][team]
				values = '"' + '","'.join(row) + '", "%s"' % (week)
				insert_string = 'INSERT INTO %s VALUES (%s)' % (stat, values)
				db.execute(insert_string)
  	return


# --------------------------------------------------------------------------- ## --------------------------------------------------------------------------- #


def fetchCSV(division, year, stat, week):
	'''
	'''
	stat_id = _stat_map[stat]

	payload = [
		('div', division),
	   	('rptWeeks', week),
	   	('statSeq', [-1, -1, stat_id, -1]),
		('sportCode', 'MLA'),
		('academicYear', year),
		('rptType', 'CSV'),
		('doWhat', 'showrankings')
	]

	response = requests.post(_BASE_URL, data=payload)
	return response.content


# --------------------------------------------------------------------------- #


def parseCSV(csv_data):
	'''
	'''
	# remove javascript from end of file
	csv_data = re.sub(r"(?is)(<script[^>]*>)(.*?)(</script>)", '', csv_data)
	
	# remove quotes
	csv_data = re.sub(r'"', '', csv_data)

	# remove header information
	csv_data = csv_data.strip().split('\n')[5:]

	all_team_data = {}

	# grab columns and data
	columns, csv_data = csv_data[0], csv_data[1:]
	columns = columns.split(',')
	for row in csv_data:
		row = row.split(',')
		all_team_data[row[1]] = row

	all_team_data['columns'] = columns

	return all_team_data


# --------------------------------------------------------------------------- #


def fetchData(division, year, start_week, end_week):
	'''
	'''
	stats_data = {}
	for stat in _stat_map:
		stats_data[stat] = {}
		for week in range(start_week, end_week+1):
			csv_data = fetchCSV(division, year, stat, week)
			parsed_data = parseCSV(csv_data)
			stats_data[stat][week] = parsed_data
	return stats_data


# --------------------------------------------------------------------------- #


def checkDB(filename):
  	'''
  	Checks to see if the database exists

  	Determines if a database with the given filename already exists
  	If so, the user has the option to (a) remove the database before
  	proceeding or (b) exit the program.  If the file does not exist,
  	simply return back to main

  	Args:
        filename: a str containing the name of the database file
  	Returns:
        None
  	'''

  	# Check if the file exists
  	if os.path.isfile(filename):

  		# Prompt the user to remove or exit and get valid input
  		prompt = ('Error: \'%s\' already exists. Do you wish to' %(filename) +
		  		  '\n\t(a) remove the database before proceeding or' +
		  	      '\n\t(b) exit the program')
  		print prompt

  		response = ''
  		while response.strip() not in ['a','b']:
  		  	response = raw_input('(a) / (b): ')

  		# Exit the program
  		if response == 'b':
  		  	print 'Exiting...'
  		  	exit(0)
		
		# Remove the file
		else:	
			os.remove(filename)
  	return


# --------------------------------------------------------------------------- #


def main():
	# Check if provided database exists
	if len(sys.argv) != 5:
		print ('Usage: python generate_data.py <division> <year> <start_week>' +
			   '<end_week>')
		print 'Invalid number of arguments. Exiting...'
		exit(1)
	division, year       = int(sys.argv[1]), int(sys.argv[2])
	start_week, end_week = int(sys.argv[3]), int(sys.argv[4]) 
	filename = 'ncaa_mlax_div_%d_%d.db' % (division, year)
  	checkDB(filename)

  	# Scrape data
	print 'Scraping lacrosse data from \'%s\'...' % (_BASE_URL)  
	stats = fetchData(division, year, start_week, end_week)
	# pp = pprint.PrettyPrinter(indent=4)
	# pp.pprint(stats)
  	
  	# Open connection to database
  	print 'Creating new lacrosse database \'%s\'...'  % (filename)
  	conn = sqlite3.connect(filename)
  
	# Deals with string issues
  	conn.text_factory = str

  	# A cursor takes in the sql commands
  	db = conn.cursor()

  	# Create the associated tables
  	createTables(db, stats)
  
  	# Insert records into db
  	print 'Inserting lacrosse data into \'%s\'...' % (filename)  
  	insertAll(db, stats)

  	# Commit changes to db
  	conn.commit()


# --------------------------------------------------------------------------- #


if __name__ == '__main__':
	main()


# --------------------------------------------------------------------------- #

