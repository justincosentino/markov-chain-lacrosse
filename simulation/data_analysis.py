def read_results_file(file_path):
	f = open(file_path, 'r')
	data = f.read_lines()
	f.close()

	print data


def main():
	file_path = './results/division_1_season_sos_25.txt'
	read_results_file(file_path)


if __name__ == '__main__':
	main()