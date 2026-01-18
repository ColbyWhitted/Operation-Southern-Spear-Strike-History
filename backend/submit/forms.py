from django import forms
from django.utils import timezone

# IMPORTANT: adjust this import to your actual Strike model location
from .models import Strike  # <-- if Strike is in the same app/models.py
# If Strike is in a different app, do: from strikes.models import Strike (or whatever app name)


class SubmitForm(forms.Form):
    description = forms.CharField(
        widget=forms.Textarea,
        label="What info is this source providing?",
        required=True,
    )

    source_url = forms.URLField(
        label="Source URL",
        required=True,
    )

    existing_strike = forms.ChoiceField(
        choices=[("new", "New Strike"), ("existing", "Existing Strike")],
        label="New or existing strike?",
        initial="existing",
        required=True,
    )

    # Safe: no DB query at import time
    strike_list = forms.ModelMultipleChoiceField(
        queryset=Strike.objects.none(),
        label="Strike List",
        required=False,
    )

    # Safe past dates: wide range, no future restriction
    new_strike_date = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(1900, timezone.now().year + 1)
        ),
        label="New Strike Date",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Safe: no assumptions about Strike fields
        self.fields["strike_list"].queryset = Strike.objects.all()
