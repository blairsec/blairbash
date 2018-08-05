from django.contrib import admin
import tagulous.admin

from .models import Quote, Vote


def approve(modeladmin, request, queryset):
	queryset.update(approved=True)
approve.short_description = 'Approve selected quotes'

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
	readonly_fields = ('timestamp',)
	list_filter = (
		('approved', admin.BooleanFieldListFilter),
	)
	search_fields = ['=id', 'content']
	actions = [approve]

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
	readonly_fields = ('timestamp',)
	search_fields = ['=quote__id', 'ip']
	list_filter = (
		('value', admin.AllValuesFieldListFilter),
	)	
