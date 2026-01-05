from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

from .models import Strike

## TODO:
## add db urls for images,
## correctly add tailwind to project
## Fix padding on "no blank is available" message
## Add headline field to model and use it to replace 
## current heading in top left table

def index(request, pk):
    template = loader.get_template('dashboard/index.html')
    context = {
        'strike': Strike.objects.get(pk=pk),
        'all_strikes': Strike.objects.all()
    }
    return HttpResponse(template.render(context, request))