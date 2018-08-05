from django.contrib import admin
import tagulous.admin

from .models import Quote, Vote

def approve(modeladmin, request, queryset):
	queryset.update(approved=True)
approve.short_description = 'Approve selected quotes'

class QuoteAdmin(admin.ModelAdmin):
	readonly_fields = ('timestamp',)
	list_filter = (
		('approved', admin.BooleanFieldListFilter),
	)
	list_display = ('id', 'approved', 'tags', 'timestamp')
	search_fields = ['=id', 'content']
	actions = [approve]
tagulous.admin.register(Quote, QuoteAdmin)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
	readonly_fields = ('timestamp',)
	list_display = ('get_quote_id', 'value', 'ip', 'timestamp')
	search_fields = ['=quote__id', 'ip']
	list_filter = (
		('value', admin.AllValuesFieldListFilter),
	)

	def get_quote_id(self, vote):
		return vote.quote.id
	get_quote_id.admin_order_field = 'quote'
	get_quote_id.short_description = 'Quote ID'

admin.site.site_header = 'Blairbash Admin'
admin.site.site_title = 'Blairbash admin'
