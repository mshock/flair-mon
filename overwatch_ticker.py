#! python

import sqlite3
from colors import red, green, yellow, magenta, cyan
import time
import os
clear = lambda: os.system('cls') if os.name == 'nt' else os.system('clear')

sleep_dur = 5
num_rows = 21
print_index = True

def get_name(css): 
	for hero in heroes: 
		if hero in css or css_lookup[hero] in css:
				return hero
	return "default"

def print_file(color, text): 
	if print_index:
		ticker_path = 'ticker.txt' 
		ticker_file = open('ticker.txt', 'a')
		ticker_file.write("<tr><td><font color='{0}'>{1}</font></td></tr>".format(color, text))
		ticker_file.close()
		
def print_end(): 
	if print_index:
		ticker_file = open('ticker.txt', 'a')
		ticker_file.write("</table></td>")
		ticker_file.close()

def print_start():		
	if print_index:
		ticker_file = open('ticker.txt', 'w')
		ticker_file.write('''<!DOCTYPE html>
	<html>
	<head>
	<meta http-equiv="refresh" content="15">
	</head>
	<body bgcolor='black'>
	<style>
		h1 {
			font-family: "Lucida Console"; 
			padding-left: 2em;
		}
		.outer{
			
		}
		
		.ticker {
			margin-left: 20em;
		}
		.ticker td{
			border: 1px solid darkgrey;
			font-size: 18pt;
			padding-left: 2px;
			padding-right: 2px;
		}

		.ticker th{
			border: 2px solid darkgrey;
			font-size: 20pt;
			color: white;
			padding-left: 2px;
			padding-right: 2px;
		}
		
		.scoreboard { 
			margin-left: 10em;
		}
		.scoreboard td {
			border: 1px solid darkgrey;
			font-size: 20pt;
			padding-left: 2px;
			padding-right: 2px;
		}
		.scoreboard th {
			border: 2px solid darkgrey;
			font-size: 22pt;
			color: white;
			padding-left: 2px;
			padding-right: 2px;
		}

	</style>
	
	<font color='white'><h1>Overwatch Flair</h1></font>
	<hr>
	<br>
	<table class='outer'><tr><td>
	<table class='ticker' cellspacing='0'><tr><th>Ticker</th></tr>
	 ''')
		#ticker_file.write(" <font color='white'>STAT\t{0:<10} -> {1:10}</font><br>\n".format('From', 'To'))
		ticker_file.close()
	
		
heroes = dict(zip('Bastion DVa Genji Hanzo Junkrat Lucio Mccree Mei Mercy Pharah Reaper Reinhardt Roadhog Soldier76 Symmetra Torbjorn Tracer Widowmaker Winston Zarya Zenyatta'.split(), [0] * 21))
css_lookup = dict(zip('DVa Symmetra Mercy Mei Lucio Winston Junkrat Roadhog Zarya Reaper Soldier76 Tracer Pharah Genji Reinhardt Mccree Widowmaker Bastion Zenyatta Torbjorn Hanzo'.split(),
		'R19 R10 R13 R18 R15 R06 R17 R16 R08 R05 R02 R14 R07 R20 R09 R04 R01 R11 R00 R03 R12'.split()))

conn = sqlite3.connect('overwatch.db')

while True:
	clear()
	print_start()
	print("\n")
	ticker = conn.execute("select flair_id, prev_id from ticker order by id desc limit {};".format(num_rows)).fetchall()

	for (to_flair, from_flair) in ticker:
		to_name = conn.execute("select name from flair where id = {}".format(to_flair)).fetchone()[0]
		to_name = get_name(to_name)
		if from_flair != 0: 
			from_name = conn.execute("select name from flair where id = {}".format(from_flair)).fetchone()[0]
			from_name = get_name(from_name)
			line = " [UPD]\t{0:<10} -> {1:<10}".format(from_name, to_name)
			if to_flair == 1: 
				print(red(line))
				print_file('red', line)
			elif to_name == from_name: 
				print(cyan(line))
				print_file('cyan', line)
			else: 
				print(yellow(line))
				print_file('yellow', line)
		else:
			line = " [NEW]\t{0:<10}".format(to_name);
			if to_flair == 1: 
				print(magenta(line))
				print_file('magenta', line)
			else:	
				print(green(line))
				print_file('green', line)
	print_end()
	time.sleep(sleep_dur)
