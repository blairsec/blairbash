from django.contrib import admin
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count, F, Q

from django.contrib.admin.models import LogEntry

admin.site.register(LogEntry)

from .models import Quote, Vote, News

def approve(modeladmin, request, queryset):
	queryset.update(approved=True)
approve.short_description = 'Approve selected quotes'

def clear_reports(modeladmin, request, queryset):
	queryset.update(reported=False)
clear_reports.short_description = 'Clear reports of selected quotes'

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):

	def score(self, quote): return quote.score
	score.admin_order_field = 'score'

	def votes(self, quote): return quote.votes
	votes.admin_order_field = 'votes'

	def get_queryset(self, request):
		return super(QuoteAdmin, self).get_queryset(request).annotate(score=Coalesce(Sum('vote__value'), 0), votes=Count('vote'))

	readonly_fields = ('timestamp', 'score', 'votes')
	list_filter = (
		('approved', admin.BooleanFieldListFilter),
		('reported', admin.BooleanFieldListFilter)
	)
	list_display = ('id', 'approved', 'reported', 'ip', 'useragent', 'timestamp', 'score', 'votes')
	search_fields = ['=id', 'content']
	actions = [approve, clear_reports]

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
	readonly_fields = ('timestamp',)
	list_display = ('get_quote_id', 'value', 'ip', 'useragent', 'timestamp')
	search_fields = ['=quote__id', 'ip']
	list_filter = (
		('value', admin.AllValuesFieldListFilter),
	)

	def get_quote_id(self, vote):
		return vote.quote.id
	get_quote_id.admin_order_field = 'quote'
	get_quote_id.short_description = 'Quote ID'

admin.site.register(News)

admin.site.site_header = 'Blairbash Admin'
admin.site.site_title = 'Blairbash admin'
