#! python

import sqlite3
import sys
import time
import os
clear = lambda: os.system('cls') if os.name == 'nt' else os.system('clear')
from colors import red, green, yellow, magenta, cyan

print_index = False

# move to config file
subreddit = 'overwatch'

conn = sqlite3.connect(subreddit + '.db')

conn_scoreboard = sqlite3.connect(subreddit + '-scoreboard.db')

conn_scoreboard.execute('''create table if not exists scoreboard
(id integer primary key autoincrement,
rank integer not null,
name text not null,
count integer,
percent real,
change integer,
shift integer,
unique (name)
)
''')

print("\ndb connection successful\n")

def print_file(color, text): 
	if print_index:
		score_path = 'scoreboard.txt' 
		score_file = open('scoreboard.txt', 'a')
		score_file.write("<tr><td><font color='{0}'>{1}</font></td></tr>".format(color, text))
		score_file.close()

def print_start():		
	if print_index:
		score_file = open('scoreboard.txt', 'w')
		score_file.write('<td><table class="scoreboard" cellspacing="0"><tr><th>Scoreboard</th></tr>')
		score_file.close()

def print_end(): 
	if print_index:
		score_file = open('scoreboard.txt', 'r')
		ticker_file = open("ticker.txt", "r")
		# ticker_file.writelines([l for l in open("scoreboard.txt").readlines() if "RANKING" in l])
		hosted_file = open('index.html','w')
		hosted_file.write(ticker_file.read())
		hosted_file.write(score_file.read())
		hosted_file.write("</table></body></html>")
		hosted_file.close()
		ticker_file.close()
		score_file.close()
		
def write_score(rank, name, count, percent, change, shift): 
	if shift == '+++':
		shift = 1
	elif shift == '---':
		shift = -1
	else: 
		shift = 0
	
	if change == '': 
		change = 0
	
	conn_scoreboard.execute("insert or replace into scoreboard (rank, name, count, percent, change, shift) values ({}, '{}', {}, {}, {}, {})".format(rank, name, count, "%.2f" % percent, change, shift))
	conn_scoreboard.commit()
		
first = True
hero_ranks = {}
hero_change = {}
hero_change2 = {}
hero_counts = {}
while True:
	clear()
	print_start()
	print("\n\n")
	counts = conn.execute('select b.name, count(a.flair_id) from user a, flair b on a.flair_id = b.id group by b.name').fetchall()
	# move css tag lookups to external file
	heroes = dict(zip('Bastion DVa Genji Hanzo Junkrat Lucio Mccree Mei Mercy Pharah Reaper Reinhardt Roadhog Soldier76 Symmetra Torbjorn Tracer Widowmaker Winston Zarya Zenyatta'.split(), [0] * 21))
	css_lookup = dict(zip('DVa Symmetra Mercy Mei Lucio Winston Junkrat Roadhog Zarya Reaper Soldier76 Tracer Pharah Genji Reinhardt Mccree Widowmaker Bastion Zenyatta Torbjorn Hanzo'.split(),
		'R19 R10 R13 R18 R15 R06 R17 R16 R08 R05 R02 R14 R07 R20 R09 R04 R01 R11 R00 R03 R12'.split()))
	total_flaired = 0
	total = 0

	for hero in heroes:
		for flair_css, count in counts:
			if hero in flair_css or css_lookup[hero] in flair_css:
				heroes[hero] += count
				total_flaired += count
	
	for i, (hero, hero_count) in enumerate(sorted(heroes.items(), key=lambda tup: tup[1], reverse=True)):
		if first:
			hero_ranks[hero] = i
			hero_change[hero] = ''
			hero_change2[hero] = ''
			hero_counts[hero] = hero_count
		
		if hero_counts[hero] < hero_count:
			hero_change2[hero] = '(+{})'.format(hero_count - hero_counts[hero])
		elif hero_counts[hero] > hero_count: 
			hero_change2[hero] = '(-{})'.format(hero_counts[hero] - hero_count)
		
		if hero_ranks[hero] < i: 
			hero_change[hero] = '---'
		elif hero_ranks[hero] > i: 
			hero_change[hero] = '+++'
		
		for hero_check in heroes:
			if hero == hero_check:
				continue
			if heroes[hero] == heroes[hero_check]:
				hero_change[hero] = ''
		
		color = red
		color_text = 'red'
		if i <= 4:
			color = green
			color_text = 'green'
		elif i < 10:
			color = yellow
			color_text = 'yellow'
		elif i < 15:
			color = magenta
			color_text = 'magenta'
		print(color("\t[{0}]\t{1:<10} : {2:<5} - {3:>5.2f}% {4:<5} {5:<3}".format(
			i+1, 
			hero, 
			hero_count, 
			(hero_count / float(total_flaired)) * 100,
			hero_change2[hero],
			hero_change[hero]
		)))
		
		write_score(i+1, hero, hero_count, (hero_count / float(total_flaired)) * 100, hero_change2[hero], hero_change[hero])
		
		print_file(color_text, "\t[{0}]\t{1:<10} : {2:<5} - {3:>5.2f}% {4:<5} {5:<3}".format(
			i+1, 
			hero, 
			hero_count, 
			(hero_count / float(total_flaired)) * 100,
			hero_change2[hero],
			hero_change[hero]
		))
		
		
		hero_ranks[hero] = i
	
	total_flaired = conn.execute('select count(1) from user where flair_id != 1').fetchone()[0];
	total_users = conn.execute('select count(1) from user').fetchone()[0];
	flair_percentage = "\n\t({0} / {1}) - {2:.2f}% users flaired".format(total_flaired, total_users, (total_flaired / float(total_users)) * 100)
	print(cyan(flair_percentage))
	print_file('cyan', flair_percentage)
	first = False
	print_end()
	time.sleep(15)


