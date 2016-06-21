#! python

import praw
import sqlite3
import time
import configparser
import sys
from colors import green, red, yellow

config = configparser.ConfigParser()
config.read('flair_parse.cfg')

print('configs parsed!')

subreddit = 'overwatch'

scan_type =  sys.argv[1] if len(sys.argv) > 1 else 'new'
after = ''
page_limit = 10
process_dups = True
user_auth = False
drop_tables = False

# TODO: refactor database connection/creation into new class/file

conn = sqlite3.connect(subreddit + '.db')

print("db connection successful")

if (drop_tables):
	conn.execute("drop table if exists user")
	conn.execute("drop table if exists flair;")
	conn.execute("drop table if exists page;")
	conn.execute("drop table if exists change;")
	conn.execute("drop table if exists ticker2;")

# TODO: add timestamps
conn.execute('''create table if not exists user
(id integer primary key autoincrement,
name text not null,
flair_id int,
foreign key(flair_id) references flair(id),
unique(name)
)
''')

conn.execute('''create table if not exists flair
(id integer primary key autoincrement,
name text not null,
unique(name)
)
''')

conn.execute('''create table if not exists page
(id integer primary key autoincrement,
name text not null,
unique(name)
)
''')

conn.execute('''create table if not exists change
(id integer primary key autoincrement,
from_flair int not null,
to_flair int not null,
count int default 0,
unique (from_flair, to_flair)
)
''')

conn.execute('''create table if not exists ticker2
(id integer primary key autoincrement,
user text not null,
flair_id int not null,
prev_id int
)
''')

# conn.execute('''create table if not exists ticker_text
# (id integer primary key autoincrement,
# user text not null,
# from_flair text not null,
# to_flair text not null
# )
# ''')

print('db tables initialized')

def print_file(color, text): 
	ticker_file = open('scoreboard.txt', 'a')
	ticker_file.write("<font color='{0}'>{1}</font><br>".format(color, text))
	ticker_file.close()


r = praw.Reddit("flair parser by u/mschock")
sub = r.get_subreddit(subreddit)

if (user_auth):
	r.set_oauth_app_info(client_id=config.get('reddit', 'client_id'), client_secret=config.get('reddit', 'client_secret'), redirect_uri='http://127.0.0.1:65010/authorize_callback')
	url = r.get_authorize_url(config.get('reddit', 'unique_key'), 'read', True)
	import webbrowser
	webbrowser.open(url)
	access_key = input("enter access key: ")
	access_information = r.get_access_information(access_key.rstrip())
	r.set_access_credentials(**access_information)

	print("user identity set!")
	# access_information = r.get_access_information('leL3zVShuR2K-Juv68KTtZ4JNtA')
	# r.set_access_credentials(**access_information)

	# r.refresh_access_information(access_information['refresh_token'])
	# authenticated_user = r.get_me()
	# print(authenticated_user.name, authenticated_user.link_karma)
else: 
	print("using anonymous identity")

p = {'after': after}

num_users = conn.execute("select count(*) from user").fetchone()[0]

running = True
first = True 
prev_after = ''
current_get_type = []
current_get_name= ['new','top','rising','hot']
while True:
	try:	
		while running:
			start_time = time.time()
			print("retrieving {0} submissions...".format(str(page_limit)))
			
			print("{0} @ {1}.{2}".format(subreddit, ('start' if after == '' else after), (scan_type + ' : ' + current_get_name[0] if scan_type == 'auto' else scan_type)))
			if first:
				current_get_type = [sub.get_new, sub.get_hot, sub.get_rising, sub.get_top]
				get_current = current_get_type[0]

			if scan_type == 'new':
				content = sub.get_new(limit=page_limit,params=p)
			elif scan_type == 'top':
				content = sub.get_top(limit=page_limit,params=p)
			elif scan_type == 'rising':
				content = sub.get_rising(limit=page_limit,params=p)
			elif scan_type == 'hot':
				content = sub.get_hot(limit=page_limit,params=p)
			elif scan_type == 'auto':
				content = get_current(limit=page_limit, params=p)
			else:
				print("unknown scan type arg: " + scan_type)
				sys.exit(1)
			
				
			print("loaded!\n")
			
			users_updated = 0 		
			num_subs = 0
			for submission in content:
				num_subs += 1
				after = submission.name
				
				# TODO: pull save user to function so that don't have to repeat updated users code etc.

				prev_after = after
				
				p['after'] = after
				process_prefix = 'NEW'
				if (conn.execute("select count(*) from page where name = '{0}'".format(after)).fetchone()[0] > 0):
					if (process_dups):
						process_prefix = "DUP"
					else:
						print("skipping duplicate: {0}".format(after))
						continue
				
				conn.execute("insert or ignore into page(name) values ('{0}')".format(after))
				comments = praw.helpers.flatten_tree(submission.comments)
				print("[{0}] parsing page: {1} - ({2}) <{3}> {4}".format(process_prefix, after, submission.score, len(comments), submission.title[:85].encode('ascii', 'replace')))
				
				# TODO: refactor insert/update, doing this for both author and commenters
				
				if (hasattr(submission,'author_flair_css_class') and submission.author_flair_css_class is not None):
						conn.execute("insert or ignore into flair(name) values ('{0}')".format(submission.author_flair_css_class))
						(flair_id, flair_name) = conn.execute("select id, name from flair where name = '{0}'".format(submission.author_flair_css_class)).fetchone()
						flair_prev = conn.execute("select flair_id from user where name = '{0}'".format(submission.author)).fetchone()
						flair_change = False
						recently_flaired = False
						if flair_prev is not None: 
							flair_prev = flair_prev[0]
							if flair_prev != flair_id:
								users_updated += 1
								flair_change = True
								conn.execute("insert or ignore into change (from_flair, to_flair) values ({0}, {1})".format(flair_prev, flair_id))
								conn.execute("update change set count = count + 1 where from_flair = {0} and to_flair = {1};".format(flair_prev, flair_id))
							else:
								flair_prev = 0
						else:
							flair_prev = 0
							recently_flaired = True
								
						conn.execute("insert or replace into user(name, flair_id) values ('{0}', {1})".format(submission.author, flair_id))
						conn.commit()
						if recently_flaired or flair_change:
							
							if (conn.execute("select count(1) from ticker2 where user = '{}' and id >= (select max(id) from ticker2) - 21".format(submission.author)).fetchone()[0] == 0):
								conn.execute("insert into ticker2(user, flair_id, prev_id) values ('{}', {}, {})".format(submission.author, flair_id, flair_prev))
								conn.commit()
				
				
				for comment in comments: 
					if (hasattr(comment,'author_flair_css_class') and comment.author_flair_css_class is not None):
						conn.execute("insert or ignore into flair(name) values ('{0}')".format(comment.author_flair_css_class))
						(flair_id, flair_name) = conn.execute("select id, name from flair where name = '{0}'".format(comment.author_flair_css_class)).fetchone()
						flair_prev = conn.execute("select flair_id from user where name = '{0}'".format(comment.author)).fetchone()
						flair_change = False
						recently_flaired = False
						if flair_prev is not None: 
							flair_prev = flair_prev[0]
							if flair_prev != flair_id:
								users_updated += 1
								flair_change = True
								conn.execute("insert or ignore into change (from_flair, to_flair) values ({0}, {1})".format(flair_prev, flair_id))
								conn.execute("update change set count = count + 1 where from_flair = {0} and to_flair = {1};".format(flair_prev, flair_id))
							else:
								flair_prev = 0
						else:
							flair_prev = 0
							recently_flaired = True
								
						conn.execute("insert or replace into user(name, flair_id) values ('{0}', {1})".format(comment.author, flair_id))
						conn.commit()
						if recently_flaired or flair_change:
							if (conn.execute("select count(1) from ticker2 where user = '{}' and id >= (select max(id) from ticker2) - 21".format(comment.author)).fetchone()[0] == 0):
								conn.execute("insert into ticker2(user, flair_id, prev_id) values ('{}', {}, {})".format(comment.author, flair_id, flair_prev))
								conn.commit()
			if num_subs == 0: 
					print('post limit reached, switching sort type and restarting...')
					current_get_type = current_get_type[-1:] + current_get_type[:-1]
					current_get_name = current_get_name[-1:] + current_get_name[:-1]
					get_current = current_get_type[0]
					after = ''
					p['after'] = ''
					continue
			sleep_time = time.time() - start_time
			sleep_time = 30 - sleep_time
			num_users_new = conn.execute("select count(*) from user").fetchone()[0]
			user_diff = num_users_new - num_users
			num_users = num_users_new
			
			print(green("\n(+{}) users added".format(user_diff)))
			print(yellow("(+{}) users updated".format(users_updated)))
			print(red("[{}] total users\n".format(num_users)))
			if(sleep_time > 0):
				print("sleeping: %f\n" % (sleep_time))
				time.sleep(sleep_time)
			first = False
	# need to catch various PRAW errors
	# TODO: figure out all the error classes and catch explicitly
	except: 
			print("\nHTTP Error (probably)")
			print("sleeping 30 seconds...\n")
			time.sleep(30)
			continue
	break
	
	
