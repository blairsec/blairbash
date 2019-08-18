from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def template_exists(name):
	try: template.loader.get_template(value)
	except template.TemplateDoesNotExist: return False
	return True
