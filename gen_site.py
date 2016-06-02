#! python

def print_start():
	html_file.write('''<!DOCTYPE html>
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
	#html_file.write(" <font color='white'>STAT\t{0:<10} -> {1:10}</font><br>\n".format('From', 'To'))

def print_color(color, text): 
	html_file.write("<tr><td><font color='{0}'>{1}</font></td></tr>".format(color, text))

def print_mid(): 
	html_file.write("</table></td>")

def print_end(): 
	hosted_file.write("</table></body></html>");

num_rows = 25
conn = sqlite3.connect('overwatch.db')
html_file = open('index.html', 'w')
print_start()
# insert ticker
print_mid()
# insert scoreboard
print_end()
html_file.close()

