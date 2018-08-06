from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.contrib import messages

from tagulous.views import autocomplete

from urlobject import URLObject

from .models import Quote, News, Vote

quotes = Quote.objects.annotate(score=Coalesce(Sum('vote__value'), 0), votes=Count('vote')).filter(approved=True)

def index(request):
	template = loader.get_template('qdb/index.html')
	context = {
		'quotes': quotes.count(),
		'news_list': News.objects.all()
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
		'previous_page': url.with_query(url.query.set_param('start', str(start-per_page if start-per_page > 0 else 0))),
		'next_page': url.with_query(url.query.set_param('start', str(start+per_page))),
		'no_pages': no_pages,
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
	
	for i in range(10): quote_list.append(quotes[random.randint(0, len(quotes)-1)])
	return get_quotes('Random Quotes', quote_list, request, no_pages=True)

def top(request):
	quote_list = quotes.order_by('-score')
	return get_quotes('Top Quotes', quote_list, request)

def bottom(request):
	quote_list = quotes.order_by('score')
	return get_quotes('Bottom Quotes', quote_list, request)

def vote_up(request, quote_id):
	if request.method == 'POST' and not request.session.get('voted', {}).get(str(quote_id), False):
		if request.session.get('voted', False) == False: request.session['voted'] = {}
		request.session['voted'][quote_id] = 'up'
		request.session.save()
		quote = get_object_or_404(Quote, pk=quote_id)
		Vote(quote=quote, ip=request.META.get('REMOTE_ADDR'), value=1).save()
		return HttpResponse('')
	else: return HttpResponse(status=403)

def vote_down(request, quote_id):
	if request.method == 'POST' and not request.session.get('voted', {}).get(str(quote_id), False):
		if request.session.get('voted', False) == False: request.session['voted'] = {}
		request.session['voted'][quote_id] = 'down'
		request.session.save()
		quote = get_object_or_404(Quote, pk=quote_id)
		Vote(quote=quote, ip=request.META.get('REMOTE_ADDR'), value=-1).save()
		return HttpResponse('')
	else: return HttpResponse(status=403)

def report(request, quote_id):
	if request.method == 'POST' and not request.session.get('reported', {}).get(str(quote_id), False):
		if request.session.get('reported', False) == False: request.session['reported'] = {}
		request.session['reported'][quote_id] = True
		request.session.save()
		quote = get_object_or_404(Quote, pk=quote_id)
		quote.reported = True
		quote.save()
		return HttpResponse('')
	else: return HttpResponse(status=403)

def quote(request, quote_id):
	quote_list = quotes.filter(id=quote_id)
	if len(quote_list) == 0: return redirect('/')
	return get_quotes('View Quote', quote_list, request, no_pages=True)

def tag_cloud(request):
	tags = Quote.tags.tag_model.objects.filter_or_initial(quote__approved=True).distinct().weight()
	template = loader.get_template('qdb/tags.html')
	context = {
		'tags': tags
	}
	return HttpResponse(template.render(context, request))

def search(request):
	template = loader.get_template('qdb/search.html')
	query = request.GET.get('q', '')
	tag = request.GET.get('tag', '')
	quote_list = quotes.filter(content__contains=query).filter(tags=tag)
	return get_quotes('Search Quotes', quote_list, request, query=query, tag=tag)

def submit(request):
	if request.method == 'POST':
		Quote(content=request.POST['content'], tags=request.POST.getlist('tags[]'), notes=request.POST['notes']).save()
		messages.success(request, 'Your quote has been sumitted for approval. An administrator will review it shortly.')
		return redirect('/submit')
	else:
		template = loader.get_template('qdb/submit.html')
		return HttpResponse(template.render({}, request))

def quote_tags_autocomplete(request):
	return autocomplete(request, Quote.tags.tag_model.objects.filter(quote__approved=True).distinct())