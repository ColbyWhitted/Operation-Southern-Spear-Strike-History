from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

from .models import Submission
from sources.models import Source
from dashboard.models import Strike
from .forms import SubmitForm

# TODO: 
# Add list of strikes back into side bar.
# Using HTMX, make the form dynamically show/hide fields based on "new" vs "existing" strike choice.
# Create thank you page after submission.
# Add strike date to front end
# clean up UI

def index(request):

    if request.method == 'POST':
        form = SubmitForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            source_url = form.cleaned_data['source_url']
            existing_strike_choice = form.cleaned_data['existing_strike']
            strike_list = form.cleaned_data['strike_list']
            new_strike_date = form.cleaned_data['new_strike_date']

            submission = Submission(
                description=description,
                source_url=source_url,
                new_strike=(existing_strike_choice == 'new'),
                new_strike_date=new_strike_date,   
                approved=False
            )

            if existing_strike_choice == 'existing' and strike_list.exists():
                submission.existing_strike = strike_list.first()

            submission.save()

            template = loader.get_template('submit/index.html')
            context = {'strike_list': Strike.objects.all(), 'form': SubmitForm(), 'success': True}
            return HttpResponse(template.render(context, request))
    else:
        form = SubmitForm()
    template = loader.get_template('submit/index.html')
    context = {
        'strike_list': Strike.objects.all(),
        'form': form
    }
    return HttpResponse(template.render(context, request))