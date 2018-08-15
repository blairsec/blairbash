from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.contrib import messages

import os
import json

from dal import autocomplete
from taggit.models import Tag

from urlobject import URLObject

from .models import Quote, News, Vote
from .charts import VoteDistributionChart

import requests

quotes = Quote.objects.annotate(score=Coalesce(Sum('vote__value'), 0), votes=Count('vote')).filter(approved=True)

def verify_recaptcha(response):
	response = requests.post('https://www.google.com/recaptcha/api/siteverify', data={ "secret": os.environ['RECAPTCHA_SECRET'], "response": ''.join(chr(x) for x in response) }).text
	return json.loads(response)['success']

def index(request):
	template = loader.get_template('qdb/index.html')
	context = {
		'quotes': quotes.count(),
		'news_list': News.objects.order_by('-timestamp')[:3]
	}
	return HttpResponse(template.render(context, request))

def news(request):
	template = loader.get_template('qdb/news.html')
	context = {
		'news_list': News.objects.order_by('-timestamp')
	}
	return HttpResponse(template.render(context, request))

def get_quotes(title, quote_list, request, per_page=10, no_pages=False, query=False, tag=False):
	start = 0
	try: start = int(request.GET.get('start', ''))
	except: pass
	if start < 0: start = 0
	if query == False: template = loader.get_template('qdb/quotes.html')
	else: template = loader.get_template('qdb/search.html')
	quotes = quote_list[start:start+per_page]
	voted = []
	reported = []
	for i in range(len(quotes)): voted.append(request.session.get('voted', {}).get(str(quotes[i].id), False)); reported.append(request.session.get('reported', {}).get(str(quotes[i].id), False))
	url = URLObject(request.build_absolute_uri())
	context = {
		'title': title,
		'quote_list': list(zip(quotes, voted, reported)),
		'previous_page': False if start - per_page < 0 else url.with_query(url.query.set_param('start', str(start-per_page if start-per_page > 0 else 0))),
		'next_page': False if start + per_page >= len(quote_list) else url.with_query(url.query.set_param('start', str(start+per_page))),
		'no_pages': no_pages,
		'verified': request.session.get('verified', False)
	}
	if query != False: context['query'] = query
	if tag != False: context['tag'] = tag
	return HttpResponse(template.render(context, request))

def latest(request):
	quote_list = quotes.order_by('-timestamp')
	return get_quotes('Latest Quotes', quote_list, request)

def random(request):
	import random
	quote_list = []
	quote_indices = random.sample(range(len(quotes)), min(10, len(quotes)))
	for i in quote_indices: quote_list.append(quotes[i])
	return get_quotes('Random Quotes', quote_list, request, no_pages=True)

def top(request):
	quote_list = quotes.order_by('-score')
	return get_quotes('Top Quotes', quote_list, request)

def bottom(request):
	quote_list = quotes.order_by('score')
	return get_quotes('Bottom Quotes', quote_list, request)

def vote_up(request, quote_id):
	if request.method == 'POST' and not request.session.get('voted', {}).get(str(quote_id), False) and (request.session.get('verified', False) or request.body and verify_recaptcha(request.body)):
		request.session['verified'] = True
		if request.session.get('voted', False) == False: request.session['voted'] = {}
		request.session['voted'][quote_id] = 'up'
		request.session.save()
		quote = get_object_or_404(Quote, pk=quote_id)
		if not quote.approved: return HttpResponse(status=403)
		Vote(quote=quote, ip=request.META.get('REMOTE_ADDR'), useragent=request.META.get('HTTP_USER_AGENT'), value=1).save()
		return HttpResponse('')
	else: return HttpResponse(status=403)

def vote_down(request, quote_id):
	if request.method == 'POST' and not request.session.get('voted', {}).get(str(quote_id), False) and (request.session.get('verified', False) or request.body and verify_recaptcha(request.body)):
		request.session['verified'] = True
		if request.session.get('voted', False) == False: request.session['voted'] = {}
		request.session['voted'][quote_id] = 'down'
		request.session.save()
		quote = get_object_or_404(Quote, pk=quote_id)
		if not quote.approved: return HttpResponse(status=403)
		Vote(quote=quote, ip=request.META.get('REMOTE_ADDR'), useragent=request.META.get('HTTP_USER_AGENT'), value=-1).save()
		return HttpResponse('')
	else: return HttpResponse(status=403)

def report(request, quote_id):
	if request.method == 'POST' and not request.session.get('reported', {}).get(str(quote_id), False) and (request.session.get('verified', False) or request.body and verify_recaptcha(request.body)):
		request.session['verified'] = True
		if request.session.get('reported', False) == False: request.session['reported'] = {}
		request.session['reported'][quote_id] = True
		request.session.save()
		quote = get_object_or_404(Quote, pk=quote_id)
		if not quote.approved: return HttpResponse(status=403)
		quote.reported = True
		quote.save()
		return HttpResponse('')
	else: return HttpResponse(status=403)

def quote(request, quote_id):
	quote_list = quotes.filter(id=quote_id)
	if len(quote_list) == 0: return redirect('/')
	return get_quotes('Quote #{}'.format(quote_id), quote_list, request, no_pages=True)

def search(request):
	template = loader.get_template('qdb/search.html')
	query = request.GET.get('q', '')
	tag = request.GET.get('tag', '')
	quote_list = quotes.filter(content__contains=query)
	if tag: quote_list = quote_list.filter(tags__name__in=[tag])
	quote_list = quote_list.order_by('-timestamp')
	return get_quotes('Search Quotes', quote_list, request, query=query, tag=tag)

def tags(request):
	tag_list = Tag.objects.filter(quote__approved=True).annotate(count=Count('quote')).order_by('name').distinct()
	max_tag = max(map(lambda tag: tag.count, tag_list))
	max_size = 35
	min_size = 15
	for tag in tag_list:
		tag.size = (tag.count/max_tag)**0.5 * (max_size-min_size) + min_size
	template = loader.get_template('qdb/tags.html')
	context = {
		'tags': tag_list,
	}
	return HttpResponse(template.render(context, request))

def stats(request):
	template = loader.get_template('qdb/stats.html')
	context = {
		'vote_distribution': VoteDistributionChart().generate()
	}
	return HttpResponse(template.render(context, request)) 

def submit(request):
	if request.method == 'POST':
		quote = Quote(content=request.POST['content'], notes=request.POST['notes'])
		quote.save()
		quote.tags.add(*request.POST.getlist('tags[]'))
		messages.success(request, 'Your quote has been submitted for approval. An administrator will review it shortly.')
		return redirect('/submit')
	else:
		template = loader.get_template('qdb/submit.html')
		return HttpResponse(template.render({}, request))

class TagAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		tags = Tag.objects.filter(quote__approved=True).annotate(count=Count('quote')).order_by('-count').distinct()
		if self.q: tags = tags.filter(name__istartswith=self.q)
		return tags

	def get_results(self, context):
		return [
		    {
		        'id': self.get_result_label(result),
		        'text': self.get_result_label(result),
		        'selected_text': self.get_selected_result_label(result),
		    } for result in context['object_list']
		]