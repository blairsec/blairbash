from django.db import models
import tagulous.models

class Quote(models.Model):
	content = models.TextField()
	tags = tagulous.models.TagField(force_lowercase=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	approved = models.BooleanField(default=False)

	def __str__(self):
		return '#' + str(self.id) + ': ' + self.content[:100].strip() + ('...' if len(self.content) > 100 else '')

class Vote(models.Model):
	ip = models.GenericIPAddressField()
	value = models.IntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)
	quote = models.ForeignKey(Quote, on_delete=models.CASCADE)

	def __str__(self):
		return ('+' if self.value >= 0 else '') + str(self.value) + ' #' + str(self.quote.id)