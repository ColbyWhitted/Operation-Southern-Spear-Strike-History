from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

from .models import Source
from dashboard.models import Strike

def index(request, strike_pk):
    template = loader.get_template('sources/index.html')
    context = {
        'strike': Strike.objects.get(pk=strike_pk),
        'all_strikes': Strike.objects.all(),
        'sources': Source.objects.filter(strike__pk=strike_pk).distinct()
    }
    return HttpResponse(template.render(context, request))