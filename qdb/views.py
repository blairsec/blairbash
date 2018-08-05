from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.db.models import Sum, Count

from .models import Quote

def index(request):
	quote_list = Quote.objects.annotate(score=Sum('vote__value'), votes=Count('vote')).filter(approved=True).order_by('-score')[:10]
	template = loader.get_template('qdb/index.html')
	context = {
		'quote_list': quote_list
	}
	return HttpResponse(template.render(context, request))
