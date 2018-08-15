from .models import Quote, Vote

import pygal

class VoteDistributionChart():

	def __init__(self):
		self.chart = pygal.Pie(
			title='Vote Distribution',
			height=400,
			width=600,
			explicit_size=True,
			margin=20,
			inner_radius=.7,
		)

	def pull(self):
		data = {}
		up = Vote.objects.filter(value=1).count()
		down = Vote.objects.filter(value=-1).count()
		data['up ({})'.format(up)] = up
		data['down ({})'.format(down)] = down
		return data

	def generate(self):
		data = self.pull()
		for key, value in data.items():
			self.chart.add(key, value)
		return self.chart.render(is_unicode=True)