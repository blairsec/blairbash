from django.core.management.base import BaseCommand

class Command(BaseCommand):

	def handle(self, **options):
		import mysql.connector
		import pytz, datetime
		import json

		objects = []

		db = mysql.connector.connect(
			host="localhost",
			user="root"
		)

		c = db.cursor()

		c.execute("USE pentau_blairbash")

		import collections
		quote_tags = collections.defaultdict(list)
		taglist = []
		c.execute("SELECT * FROM chirpy_quote_tag")
		for t in c:
			taglist.append(t[1])
			quote_tags[t[0]].append(t[1])

		# import tags
		tags = {}
		replace_tags = {}
		c.execute("SELECT * FROM chirpy_tags")
		current = []
		ids = []
		for t in c:
			try:
				current.index(t[1])
				continue
				replace_tags[t[0]] = ids[current.index(t[1])]
			except:
				current.append(t[1]); ids.append(t[0])
				tag = {
					"pk": t[0],
					"model": "taggit.Tag",
					"fields": {
						"name": t[1],
						"slug": t[1]
					}
				}
				objects.append(tag)
				#print(json.dumps(tag, indent=4, separators=(',', ': ')))
		for r in replace_tags:
			for i in quote_tags:
				if quote_tags[i] == r:
					quote_tags[i] = replace_tags[r]
			for i in taglist:
				if taglist[i] == r:
					taglist[i] = replace_tags[r]


		vote_id = 1
		# import quotes
		c.execute("SELECT * from chirpy_quotes")
		for q in c:
			quote = {
				"pk": q[0],
				"model": "qdb.quote",
				"fields": {
					"approved": q[6],
					"content": q[1],
					"notes": q[2] if q[2] else "",
					"reported": q[7],
					"timestamp": pytz.timezone('US/Eastern').localize(q[5], is_dst=False).astimezone(pytz.utc).isoformat().replace('+00:00', 'Z')
				}
			}
			objects.append(quote)
			# create up votes
			for i in range((q[3] + q[4])//2):
				vote = {
					"model": "qdb.vote",
					"pk": vote_id,
					"fields": {
						"ip": "0.0.0.0",
						"quote": q[0],
						"timestamp": quote["fields"]["timestamp"],
						"useragent": "",
						"value": 1
					}
				}
				objects.append(vote)
				vote_id += 1
			# create down votes
			for i in range((q[4] - q[3])//2):
				vote = {
					"model": "qdb.vote",
					"pk": vote_id,
					"fields": {
						"ip": "0.0.0.0",
						"quote": q[0],
						"timestamp": quote["fields"]["timestamp"],
						"useragent": "",
						"value": -1
					}
				}
				objects.append(vote)
				vote_id += 1
			#print(json.dumps(quote, indent=4, separators=(',', ': ')))

		# associate tags with quotes
		for q in quote_tags:
			item = {

			}

		# load usernames
		id_to_user = {}
		c.execute("SELECT * FROM chirpy_accounts")
		for u in c:
			id_to_user[u[0]] = u[1]

		# import news
		c.execute("SELECT * FROM chirpy_news")
		for n in c:
			news = {
				"model": "qdb.news",
				"pk": n[0],
				"fields": {
					"author": id_to_user[n[2]] if n[2] else "Unknown",
					"content": n[1],
					"timestamp": pytz.timezone('US/Eastern').localize(n[3], is_dst=False).astimezone(pytz.utc).isoformat().replace('+00:00', 'Z')
				}
			}
			objects.append(news)

		json.dump(objects, open("chirpy.json", "w"))

		c.execute("show tables")
		for t in c:
			print(t)
