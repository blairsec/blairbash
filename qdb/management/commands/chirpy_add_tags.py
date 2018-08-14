from django.core.management.base import BaseCommand

class Command(BaseCommand):

	def handle(self, **options):
		import mysql.connector
		import collections

		from qdb.models import Quote

		db = mysql.connector.connect(
			host="localhost",
			user="root"
		)

		c = db.cursor()
		c.execute("USE pentau_blairbash")

		# import tags
		tags = {}
		c.execute("SELECT * FROM chirpy_tags")
		for t in c:
			if t[1]: tags[t[0]] = t[1]
		quote_tags = collections.defaultdict(list)
		c.execute("SELECT * FROM chirpy_quote_tag")
		for t in c:
			if tags.get(t[1]): quote_tags[t[0]].append(tags[t[1]])

		# add tags to quotes
		quotes = Quote.objects.all()
		for quote in quotes:
			quote.tags.add(*quote_tags[quote.id])