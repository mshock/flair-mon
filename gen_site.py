#!/usr/bin/python

import sqlite3
import time

# TODO: bring into config file 
num_rows = 21

def print_start():
	total_flaired = conn.execute("select count(1) from user where flair_id != 1").fetchone()[0]
	total_users = conn.execute("select count(1) from user").fetchone()[0]
	html_file.write('''<!DOCTYPE html>
	<html>
	<head>
	<title>Overwatch Flair</title>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.2/jquery.min.js"></script>
	<script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
	<script src="./assets/refresh.js"></script>
	</head>
	<style>
		body {
			background-color: darkgrey;
			font-family: 'Lucida Console', Monaco, monospace;
			font-weight: bold;
		}
		h5 {
			color: #eee;
			}
		h4 {color: darkgrey}
		h3 {text-align: center;}
		.scoreboard {
			background-color: lightgrey;
			border-radius: 25px;
			border: 1px solid SlateGrey;
			}
		table { border-collapse: separate; }
		tr:first-child td:first-child { border-top-left-radius: 10px; }
		tr:first-child td:last-child { border-top-right-radius: 10px; }
		tr:last-child td:first-child { border-bottom-left-radius: 10px; }
		tr:last-child td:last-child { border-bottom-right-radius: 10px; }
		.ticker {
			background-color: lightgrey;
			border-radius: 25px;
			border: 1px solid SlateGrey;
			}
		.logo {
			max-height: 50%;
			max-width: 50%;
		}
		.jumbotron {
			border: 1px solid SlateGrey;
			margin-top: 5px;
			margin-bottom: 15px;
			padding: 5px;
		}
		a {
			color: royalblue;
		}
		a:hover {
			color: goldenrod;
		}
		a:visited{ text-decoration: none;}
		a:active { text-decoration: none;}
		.user_counts{ }
		
	</style>
	''' +
	'''
	<div class='container'>
		<div class='jumbotron'>
		<div class='table-responsive'>
				<table>
				<tr>
				<td>
				<a href='http://www.reddit.com/r/overwatch'>
					<img src='./assets/logo.png' class='img-responsive' alt='Overwatch Logo' class='logo' height='50%' width='50%'>
				</a>
				</td>
				<td style='white-space:nowrap'>
				<a href='http://www.reddit.com/r/overwatch'><h2>/r/Overwatch Flair</h2></a>
				
				</td>
				<td style='white-space:nowrap; padding-left: 2em; padding-top: 1em;' class='user_counts'>
				<h4>( refreshes automatically )</h4>
					<table>
					<tr>
					<td>
					( <font color='DarkGreen'>{0:<6} </font> / <font color='DarkRed'> {1:<6} </font>) - <font color='GoldenRod'>{2:>3.2f}%</font> users flaired
					</td>
					</tr>
					</table>
				</td>
				<td style='padding-left:1em;'>
				<h5>cobbled together by /u/mschock</h5>
				</td>
				</tr></table>
		</div>
		</div>
		
	 '''.format(total_flaired, total_users, (total_flaired / float(total_users)) * 100))
	
def print_end(): 
	html_file.write("</div></div><br></body></html>")


def print_color(color, text): 
	html_file.write("<tr><font color='{0}'>{1}</font></tr>".format(color, text))


	
def print_ticker(): 
	ticks = conn.execute("select a.user, b.name, c.name from ticker2 a join flair b on b.id = a.flair_id left join flair c on c.id = a.prev_id order by a.id desc limit {}".format(num_rows)).fetchall()
	html_file.write('''
		<div class='col-xs-6 ticker'>
		<div class='table-responsive'>
		<h3 class='sub-header'>Ticker</h3>
		<table class='table table-striped'>
		<tr>
			<th>Type</th>
			<th>User</th>
			<th>From</th>
			<th></th>
			<th>To</th>
		</tr>
	''')
	
	for user, flair_to, flair_from in ticks:
		if flair_from is not None:
			flair_from = get_name(flair_from)
		flair_to = get_name(flair_to)
		tick_type = 'UPD'
		tick_color = 'DarkOrange'
		if flair_from is None and flair_to == 'default': 
			tick_type = 'NEW'
			tick_color = 'Green'
		elif flair_to != 'default' and flair_from is None:
			tick_type = 'UPD'
			tick_color = 'RoyalBlue'
		elif flair_from == flair_to:
			tick_type = 'UPD'
			tick_color = 'Sienna'
		elif flair_to != 'default': 
			tick_type = 'UPD'
			tick_color = 'FireBrick'
		
		html_file.write("<tr style='color:{}'><td>[{}]</td><td>{}</td><td>{}</td><td>>></td><td>{}</td></tr>\n".format(tick_color, tick_type, user, flair_from, flair_to))
		
	html_file.write("</table></div></div>")

def print_scoreboard(): 
	scores = conn_scoreboard.execute("select rank, name, count, percent, change, shift from scoreboard order by rank asc").fetchall()
	
	html_file.write('''
	<div class='col-xs-6 scoreboard'>
	<div class='table-responsive'>
	<h3 class='sub-header'>Scoreboard</h3>
	<table class='table table-striped'>
	<tr>
	<th>Rank</th>
	<th>Hero</th>
	<th>Count</th>
	<th>Percent</th>
	<th>Change</th>
	<th></th>
	</tr>
	''')
	
	for rank, name, count, percent, change, shift in scores: 
		score_color = 'FireBrick'
		if rank <= 5: 
			score_color = 'Green'
		elif rank <= 10:
			score_color = 'RoyalBlue'
		elif rank <= 15: 
			score_color = 'Sienna'

		shift_text = ''
		if shift == 1: 
			shift_text = '+++'
		elif shift == -1:
			shift_text = '---'
		
		if change >= 0: 
			change = '+' + str(change)
		
		html_file.write("<tr style='color:{}'><td>[{}]</td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}</td></tr>\n".format(score_color, rank, name, count, percent, change, shift_text))
		
	html_file.write("</table></div></div>")

def get_name(css): 
	for hero in heroes: 
		if hero in css or css_lookup[hero] in css:
				return hero
	return "default"

heroes = dict(zip('Bastion DVa Genji Hanzo Junkrat Lucio Mccree Mei Mercy Pharah Reaper Reinhardt Roadhog Soldier76 Symmetra Torbjorn Tracer Widowmaker Winston Zarya Zenyatta'.split(), [0] * 21))
css_lookup = dict(zip('DVa Symmetra Mercy Mei Lucio Winston Junkrat Roadhog Zarya Reaper Soldier76 Tracer Pharah Genji Reinhardt Mccree Widowmaker Bastion Zenyatta Torbjorn Hanzo'.split(),
	'R19 R10 R13 R18 R15 R06 R17 R16 R08 R05 R02 R14 R07 R20 R09 R04 R01 R11 R00 R03 R12'.split()))

conn = sqlite3.connect('overwatch.db')
conn_scoreboard = sqlite3.connect('overwatch-scoreboard.db')
while True:
	html_file = open('index.html', 'w')
	print_start()
	# insert ticker
	print_ticker()
	# insert scoreboard
	print_scoreboard()
	print_end()
	html_file.close()
	print("static page regenerated, sleeping 5 seconds...")
	time.sleep(5)
