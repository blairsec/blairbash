from django.contrib import admin
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count, F, Q, Exists, OuterRef

from django.utils.translation import gettext_lazy as _ 

from django.contrib.admin.models import LogEntry

admin.site.register(LogEntry)

from .models import Quote, Vote, News, Report

def approve(modeladmin, request, queryset):
	queryset.update(approved=True)
approve.short_description = 'Approve selected quotes'

class ReportedListFilter(admin.SimpleListFilter):

	title = _('reported')
	parameter_name = 'reported'

	def lookups(self, request, model_admin):
		return (('1', _('Yes')), ('0', _('No')))

	def queryset(self, request, queryset):
		if self.value() == '1': return queryset.filter(reported=True)
		if self.value() == '0': return queryset.filter(reported=False)

class ReportInline(admin.TabularInline):
	model = Report
	extra = 0
	readonly_fields = ('timestamp',)
	fields = ('ip', 'timestamp', 'reason')

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):

	inlines = [ReportInline]

	def score(self, quote): return quote.score
	score.admin_order_field = 'score'

	def votes(self, quote): return quote.votes
	votes.admin_order_field = 'votes'

	def reported(self, quote): return quote.reported
	reported.admin_order_field = 'reported'
	reported.boolean = True

	def get_queryset(self, request):
		return super(QuoteAdmin, self).get_queryset(request).annotate(score=Coalesce(Sum('vote__value'), 0), votes=Count('vote'), reported=Exists(Report.objects.filter(quote=OuterRef('id'))))

	readonly_fields = ('timestamp', 'score', 'votes')
	list_filter = (
		('approved', admin.BooleanFieldListFilter),
		ReportedListFilter
		
	)
	list_display = ('id', 'approved', 'reported', 'ip', 'useragent', 'timestamp', 'score', 'votes')
	search_fields = ['=id', 'content']
	actions = [approve]

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

admin.site.register(Report)

admin.site.site_header = 'Blairbash Admin'
admin.site.site_title = 'Blairbash admin'
