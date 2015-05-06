'''
'''


# ---------------------------------------------------------------------------- #


from bs4 import BeautifulSoup as bs
import requests
import sqlite3
import time
import sys
import os
import re


# ---------------------------------------------------------------------------- #


_BASE_URL    = 'http://www.laxpower.com'


# ---------------------------------------------------------------------------- #
# DATABASE INTERFACE


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


def createTable(db, longest_name):
  	# Create tables
  	try:
		db.execute( '''CREATE TABLE Schedule
					   (
					  	team_name   VARCHAR(%d),
					  	game_date   VARCHAR(5),
					  	location    VARCHAR(1),
					  	opp_name    VARCHAR(%d),
					  	team_score  INT,
					  	opp_score   INT,
					  	game_number INT,
					  	PRIMARY KEY (team_name, game_number)
					   )
					''' %(longest_name, longest_name))

  	except sqlite3.Error as e:
  		print 'An error has occured: %s' % (e.args[0])
  		print 'Exiting...'
  		if db: db.close()
  		exit(1)
  	return


def entryGenerator(team_data):
	for team in team_data:
		for i, game in enumerate(team):
			game.append(i)
			yield tuple(game)
			

def insertAll(db, team_data):
	insert_str = '''INSERT INTO Schedule 
					(
					team_name, game_date, location, opp_name, 
					team_score, opp_score, game_number
					) VALUES (?, ?, ?, ?, ?, ?, ?)
				 '''
	db.executemany(insert_str, entryGenerator(team_data))
	return 




# ---------------------------------------------------------------------------- #
# SCRAPING INTERFACE


def find_longest_name(team_data):
	longest_name = 0
	name = ''
	for team in team_data:
		if len(team[0][0]) > longest_name:
			longest_name = len(team[0][0])
			name = team[0][0]
	return longest_name, name


def get_team_ids(_RATINGS_URL):
	response = requests.get(_BASE_URL + _RATINGS_URL)
	teams = re.findall('"(.*?PHP)">(.*?)<',response.content)
	teams = list(set(teams))
	teams = [{'id':t[0],'name':t[1]} for t in teams]
	return teams


def get_team_page(team, _TEAM_URL):
    team_url='%s%s%s?tab=detail' % (_BASE_URL, _TEAM_URL, team['id'])
    team_detail_html = requests.get(team_url).content
    team_soup = bs(team_detail_html.decode('utf-8', 'ignore'))
    table = team_soup.find("table")
    rows=[]
    for row in table.find_all("tr")[3:-1]:
        data=[d.get_text().replace(u'\xa0\x96','') for d in row.findAll('td')]
        outline=[team['name']]+data[:5]
        rows.append([i.encode('utf-8') for i in outline])

    # Naming errors
    for item in rows:
    	if item[0] == 'Loyola': item[0] = 'Loyola Maryland'
    	if item[3] == 'Loyola': item[3] = 'Loyola Maryland'

    	if item[0] == 'Army': item[0] = 'Army West Point'
    	if item[3] == 'Army': item[3] = 'Army West Point'

    	if item[0] == 'Albany': item[0] = 'Albany (NY)'
    	if item[3] == 'Albany': item[3] = 'Albany (NY)'

    	if item[0] == 'Penn State': item[0] = 'Penn St.'
    	if item[3] == 'Penn State': item[3] = 'Penn St.'

    	if item[0] == "St. John's": item[0] = "St. John's (NY)"
    	if item[3] == "St. John's": item[3] = "St. John's (NY)"
    	
    	if item[0] == "Mount St. Mary's": item[0] = "Mt. St. Mary's"
    	if item[3] == "Mount St. Mary's": item[3] = "Mt. St. Mary's"
    	
    	if item[0] == "Ohio State": item[0] = "Ohio St."
    	if item[3] == "Ohio State": item[3] = "Ohio St."


    return rows 


# ---------------------------------------------------------------------------- #


def main():
	# Check provided args 
	if len(sys.argv) != 3:
		print 'Usage: python generate_schedule.py <division> <year>'
		print 'Invalid number of arguments. Exiting...'
		exit(1)
	elif int(sys.argv[1]) not in range(1,4):
		print 'Usage: python generate_schedule.py <division> <year>'
		print '<division> must be [1,2,3]. Exiting...'
		exit(1)

	# Get args and update urls and database name
	division, year = sys.argv[1], sys.argv[2][2:]
	_RATINGS_URL = '/update%s/binmen/rating0%s.php' % (year, division)
	_TEAM_URL    = '/update%s/binmen/' % (year)

	# Check if database exists
	filename = 'ncaa_mlax_div_%s_20%s_sched.db' % (division, year)
	checkDB(filename)

	# Scrape data for a given year
	print 'Scraping lacrosse schedule data from \'%s\'...' % (_BASE_URL)  
	team_list = get_team_ids(_RATINGS_URL)
	team_data = []
	for team in team_list:
		team_data.append(get_team_page(team, _TEAM_URL))
		# time.sleep(1)

	# Add to sqlite database
  	print 'Creating new lacrosse schedule database \'%s\'...'  % (filename)
	conn = sqlite3.connect(filename)
  
	# Deals with string issues
  	conn.text_factory = str

  	# A cursor takes in the sql commands
  	db = conn.cursor()

  	# Create the associated tables
  	longest_name, name = find_longest_name(team_data)
  	createTable(db, longest_name)

  	# Insert team data
  	insertAll(db, team_data)
	
	# Commit changes to db
  	conn.commit()


# ---------------------------------------------------------------------------- #


if __name__ == '__main__':
	main()


# ---------------------------------------------------------------------------- #

