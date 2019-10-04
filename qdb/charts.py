from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.utils.timezone import localtime

from .models import Quote, Vote

import pygal

from pygal.style import Style
style = Style(
	background='transparent',
	plot_background='transparent',
	foreground='#3d3d3d',
	foreground_strong='#303030',
	foreground_subtle='#939393',
	opacity='.8',
	opacity_hover='.9',
	colors=('#fa5555', '#888'),
	label_font_size=15,
	major_label_font_size=15,
	title_font_size=20,
	legend_font_size=15
)

MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

quotes = Quote.objects.annotate(score=Coalesce(Sum('vote__value'), 0), votes=Count('vote')).filter(approved=True)
votes = Vote.objects

class QuotesOverTime():

	def __init__(self):
		self.chart = pygal.DateTimeLine(
			title='Quotes over Time',
			x_label_rotation=90,
			x_value_formatter=lambda dt: dt.strftime('%b %Y'),
			margin=20,
			show_legend=False,
			show_dots=False,
			fill=True,
			style=style
		)

	def pull(self):
		data = {}
		for quote in quotes.order_by('timestamp'):
			timestamp = quote.timestamp.timestamp()
			data[timestamp] = data.get(timestamp, 0)
			data[timestamp] += 1
		return data

	def generate(self):
		data = self.pull()
		points = []
		total = 0
		for key, value in data.items():
			points.append((key, total))
			total += value
		self.chart.add('quotes', points)
		return self.chart.render(is_unicode=True)

class QuotesByHour():

	def __init__(self):
		self.chart = pygal.Bar(
			title='Quotes by Hour',
			x_labels = list(map(str, range(24))),
			margin=20,
			show_legend=False,
			style=style
		)

	def pull(self):
		data = [0 for _ in range(24)]
		for quote in quotes:
			data[localtime(quote.timestamp).hour] += 1
		return data

	def generate(self):
		data = self.pull()
		self.chart.add('quotes', data)
		return self.chart.render(is_unicode=True)

class QuotesByMonth():

	def __init__(self):
		self.chart = pygal.Bar(
			title='Quotes by Month',
			x_labels = MONTHS,
			margin=20,
			show_legend=False,
			style=style
		)

	def pull(self):
		data = [0 for _ in range(12)]
		for quote in quotes:
			data[localtime(quote.timestamp).month-1] += 1
		return data

	def generate(self):
		data = self.pull()
		self.chart.add('quotes', data)
		return self.chart.render(is_unicode=True)

class QuotesByRating():

	def __init__(self):
		self.chart = pygal.Histogram(
			title='Quotes by Rating',
			margin=20,
			show_legend=False,
			style=style
		)

	def pull(self):
		data = {}
		for quote in quotes:
			data[quote.score] = data.get(quote.score, 0)
			data[quote.score] += 1
		return data

	def generate(self):
		data = self.pull()
		bars = []
		for key, value in data.items():
			bars.append((value, key, key+1))
		self.chart.add('quotes', bars)
		return self.chart.render(is_unicode=True)

class VoteDistribution():

	def __init__(self):
		self.chart = pygal.Pie(
			title='Vote Distribution',
			margin=20,
			inner_radius=.7,
			style=style
		)

	def pull(self):
		data = {}
		up = votes.filter(value=1).count()
		down = votes.filter(value=-1).count()
		data['up'] = up
		data['down'] = down
		return data

	def generate(self):
		data = self.pull()
		for key, value in data.items():
			self.chart.add('{} ({})'.format(key, value), value)
		return self.chart.render(is_unicode=True)
