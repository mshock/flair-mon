#! python

import sqlite3

def print_start():
	html_file.write('''<!DOCTYPE html>
	<html>
	<head>
	<title>Overwatch Flair</title>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.2/jquery.min.js"></script>
	<script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
	</head>
	<style>
		body {
			background-color: lightgrey;
			font-family: 'Lucida Console', Monaco, monospace;
		}
		h4 {color: darkgrey}
	</style>
	<br>
	<div class='container'>
		<div class='jumbotron'>
			<h1>Overwatch Flair</h1>
			<h4>(refreshes every 15 seconds)</h4>
		</div>
		
	 ''')
	
def print_end(): 
	html_file.write("</div></div></body></html>")


def print_color(color, text): 
	html_file.write("<tr><font color='{0}'>{1}</font></tr>".format(color, text))


	
def print_ticker(): 
	ticks = conn.execute("select a.user, b.name, c.name from ticker2 a join flair b on b.id = a.flair_id left join flair c on c.id = a.prev_id order by a.id desc limit 100").fetchall()
	html_file.write('''
	<div class='col-xs-6'>
	<h2 class='sub-header'>Ticker</h2>
	<table class='table table-striped'>
	''')
	for user, flair_to, flair_from in ticks:
		tick_type = 'UPD'
		tick_color = 'FireBrick'
		if flair_from is None and flair_to == 'default': 
			tick_type = 'NEW'
			tick_color = 'Green'
		elif flair_to != 'default':
			tick_type = 'UPD'
			tick_color = 'GoldenRod'
		
		html_file.write("<tr style='color:{}'><td>[{}]</td><td>{}</td><td>{}</td><td>>></td><td>{}</td></tr>\n".format(tick_color, tick_type, user, flair_from, flair_to))
		
	html_file.write("</table></div>")
num_rows = 25
conn = sqlite3.connect('overwatch.db')
conn_scoreboard = sqlite3.connect('overwatch-scoreboard.db')
html_file = open('index.html', 'w')
print_start()
# insert ticker
print_ticker()
# insert scoreboard
print_end()
html_file.close()

