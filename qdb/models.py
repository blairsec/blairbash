from django.db import models
import tagulous.models

class Quote(models.Model):
	content = models.TextField()
	tags = tagulous.models.TagField(force_lowercase=True)
	timestamp = models.DateTimeField(auto_now_add=True)

class Vote(models.Model):
	ip = models.GenericIPAddressField()
	value = models.IntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)
	quote = models.ForeignKey(Quote, on_delete=models.CASCADE)