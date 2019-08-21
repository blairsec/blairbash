from django.urls import path, re_path

from . import views
from .models import Quote

from dal import autocomplete

urlpatterns = [
	path('', views.index, name='index'),
	path('latest', views.latest, name='latest'),
	path('random', views.random, name='random'),
	path('top', views.top, name='top'),
	path('bottom', views.bottom, name='bottom'),
	path('tags', views.tags, name='tags'),
	path('search', views.search, name='search'),
	path('stats', views.stats, name='stats'),
	path('submit', views.submit, name='submit'),
	path('news', views.news, name='news'),
	path('about', views.about, name='about'),
	re_path(r'^quotes\.(?:json|csv)$', views.api, name='api'),
	path('tags/autocomplete', views.TagAutocomplete.as_view(model=Quote), name='quote_tags_autocomplete'),
	path('<int:quote_id>', views.quote, name='quote'),
	path('<int:quote_id>/up', views.vote_up),
	path('<int:quote_id>/down', views.vote_down),
	path('<int:quote_id>/report', views.report)
]
