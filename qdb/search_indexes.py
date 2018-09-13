import datetime
from haystack import indexes
from .models import Quote


class QuoteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    content = indexes.CharField(model_attr='content')
    timestamp = indexes.DateTimeField(model_attr='timestamp')
    approved = indexes.BooleanField(model_attr='approved')
    id = indexes.IntegerField(model_attr='id')

    def get_model(self):
        return Quote

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(approved=True)
