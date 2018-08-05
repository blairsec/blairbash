from django.contrib import admin

from .models import Quote, Vote

class QuoteAdmin(admin.ModelAdmin):
	readonly_fields = ('timestamp',)

admin.site.register(Quote, QuoteAdmin)

class VoteAdmin(admin.ModelAdmin):
	readonly_fields = ('timestamp',)

admin.site.register(Vote, VoteAdmin)