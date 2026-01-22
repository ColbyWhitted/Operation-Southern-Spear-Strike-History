from django.test import TestCase, Client
from submit.models import Submission
from submit.forms import SubmitForm
from dashboard.models import Strike
from datetime import date
from decimal import Decimal


class SubmissionModelTests(TestCase):
    """Test Submission model."""

    def setUp(self):
        self.strike = Strike.objects.create(
            date=date(2024, 1, 15),
            location_label="Test Strike",
            location_lat=Decimal("12.34567890123456"),
            location_lon=Decimal("-98.76543210987654"),
            target="Test Target",
            striker="Test Striker",
        )

    def test_submission_creation(self):
        """Submission is created with required fields."""
        submission = Submission.objects.create(
            description="Test description",
            source_url="https://example.com/source",
        )
        self.assertEqual(submission.description, "Test description")
        self.assertEqual(submission.source_url, "https://example.com/source")
        self.assertFalse(submission.approved)
        self.assertFalse(submission.new_strike)

    def test_submission_str_representation(self):
        """Submission __str__ returns description and pk."""
        submission = Submission.objects.create(
            description="Test submission",
            source_url="https://example.com",
        )
        expected = f"{submission.description} - {submission.pk}"
        self.assertEqual(str(submission), expected)

    def test_submission_auto_timestamp(self):
        """submitted_at is automatically set on creation."""
        submission = Submission.objects.create(
            description="Test",
            source_url="https://example.com",
        )
        self.assertIsNotNone(submission.submitted_at)

    def test_submission_ordering(self):
        """Submissions ordered by -submitted_at (newest first)."""
        sub1 = Submission.objects.create(
            description="First",
            source_url="https://example.com/1",
        )
        sub2 = Submission.objects.create(
            description="Second",
            source_url="https://example.com/2",
        )
        submissions = list(Submission.objects.all())
        # Most recently created should be first
        self.assertEqual(submissions[0], sub2)
        self.assertEqual(submissions[1], sub1)

    def test_submission_strike_relationship(self):
        """Submission can link to existing strike."""
        submission = Submission.objects.create(
            description="About existing strike",
            source_url="https://example.com",
            existing_strike=self.strike,
            new_strike=False,
        )
        self.assertEqual(submission.existing_strike, self.strike)

    def test_submission_strike_set_null_on_delete(self):
        """existing_strike set to NULL when strike deleted."""
        submission = Submission.objects.create(
            description="Test",
            source_url="https://example.com",
            existing_strike=self.strike,
        )
        strike_pk = self.strike.pk
        self.strike.delete()
        submission.refresh_from_db()
        self.assertIsNone(submission.existing_strike)

    def test_submission_new_strike_fields(self):
        """Submission can have new_strike and new_strike_date."""
        submission = Submission.objects.create(
            description="New strike info",
            source_url="https://example.com",
            new_strike=True,
            new_strike_date=date(2024, 3, 15),
        )
        self.assertTrue(submission.new_strike)
        self.assertEqual(submission.new_strike_date, date(2024, 3, 15))


class SubmitFormTests(TestCase):
    """Test SubmitForm validation and behavior."""

    def setUp(self):
        self.strike = Strike.objects.create(
            date=date(2024, 1, 15),
            location_label="Form Test Strike",
            location_lat=Decimal("12.34567890123456"),
            location_lon=Decimal("-98.76543210987654"),
            target="Test Target",
            striker="Test Striker",
        )

    def test_form_valid_with_existing_strike(self):
        """Form is valid when selecting existing strike."""
        form = SubmitForm(data={
            'description': 'Test description for existing strike',
            'source_url': 'https://example.com/source',
            'existing_strike': 'existing',
            'strike_list': [self.strike.pk],
        })
        self.assertTrue(form.is_valid())

    def test_form_valid_with_new_strike(self):
        """Form is valid when selecting new strike with date."""
        form = SubmitForm(data={
            'description': 'Test description for new strike',
            'source_url': 'https://example.com/source',
            'existing_strike': 'new',
            'new_strike_date_year': '2024',
            'new_strike_date_month': '6',
            'new_strike_date_day': '15',
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_description(self):
        """Form requires description."""
        form = SubmitForm(data={
            'source_url': 'https://example.com',
            'existing_strike': 'new',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_form_invalid_without_source_url(self):
        """Form requires source_url."""
        form = SubmitForm(data={
            'description': 'Test description',
            'existing_strike': 'new',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('source_url', form.errors)

    def test_form_invalid_with_bad_url(self):
        """Form validates URL format."""
        form = SubmitForm(data={
            'description': 'Test',
            'source_url': 'not-a-valid-url',
            'existing_strike': 'new',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('source_url', form.errors)

    def test_form_strike_list_queryset(self):
        """strike_list field contains all strikes after init."""
        form = SubmitForm()
        self.assertIn(self.strike, form.fields['strike_list'].queryset)

    def test_form_existing_strike_choices(self):
        """existing_strike has 'new' and 'existing' choices."""
        form = SubmitForm()
        choices = [c[0] for c in form.fields['existing_strike'].choices]
        self.assertIn('new', choices)
        self.assertIn('existing', choices)

    def test_form_existing_strike_default(self):
        """existing_strike defaults to 'existing'."""
        form = SubmitForm()
        self.assertEqual(form.fields['existing_strike'].initial, 'existing')


class SubmitViewTests(TestCase):
    """Test submit views."""

    def setUp(self):
        self.client = Client()
        self.strike = Strike.objects.create(
            date=date(2024, 1, 15),
            location_label="View Test Strike",
            location_lat=Decimal("12.34567890123456"),
            location_lon=Decimal("-98.76543210987654"),
            target="Test Target",
            striker="Test Striker",
        )

    def test_index_get_returns_200(self):
        """GET request returns 200 with form."""
        response = self.client.get('/submit/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], SubmitForm)

    def test_index_get_uses_correct_template(self):
        """Index view uses submit/index.html template."""
        response = self.client.get('/submit/')
        self.assertTemplateUsed(response, 'submit/index.html')

    def test_index_get_context_contains_strike_list(self):
        """GET request context includes strike_list."""
        response = self.client.get('/submit/')
        self.assertIn(self.strike, response.context['strike_list'])

    def test_index_post_creates_submission_existing_strike(self):
        """Valid POST with existing strike creates Submission."""
        data = {
            'description': 'New submission test',
            'source_url': 'https://example.com/new-source',
            'existing_strike': 'existing',
            'strike_list': [self.strike.pk],
        }
        initial_count = Submission.objects.count()
        response = self.client.post('/submit/', data)

        self.assertEqual(Submission.objects.count(), initial_count + 1)
        submission = Submission.objects.first()
        self.assertEqual(submission.description, 'New submission test')
        self.assertEqual(submission.existing_strike, self.strike)
        self.assertFalse(submission.new_strike)

    def test_index_post_creates_submission_new_strike(self):
        """Valid POST with new strike creates Submission."""
        data = {
            'description': 'New strike submission',
            'source_url': 'https://example.com/new-strike',
            'existing_strike': 'new',
            'new_strike_date_year': '2024',
            'new_strike_date_month': '3',
            'new_strike_date_day': '20',
        }
        initial_count = Submission.objects.count()
        response = self.client.post('/submit/', data)

        self.assertEqual(Submission.objects.count(), initial_count + 1)
        submission = Submission.objects.first()
        self.assertTrue(submission.new_strike)
        self.assertEqual(submission.new_strike_date, date(2024, 3, 20))
        self.assertIsNone(submission.existing_strike)

    def test_index_post_success_shows_success_context(self):
        """Successful POST returns success in context."""
        data = {
            'description': 'Success test',
            'source_url': 'https://example.com/success',
            'existing_strike': 'new',
            'new_strike_date_year': '2024',
            'new_strike_date_month': '1',
            'new_strike_date_day': '1',
        }
        response = self.client.post('/submit/', data)
        self.assertTrue(response.context.get('success'))

    def test_index_post_invalid_shows_errors(self):
        """Invalid POST re-renders form with errors."""
        response = self.client.post('/submit/', {
            'description': '',
            'source_url': 'https://example.com',
            'existing_strike': 'new',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())


class StrikeFieldsHTMXViewTests(TestCase):
    """Test HTMX endpoint for dynamic form fields."""

    def setUp(self):
        self.client = Client()
        self.strike = Strike.objects.create(
            date=date(2024, 1, 15),
            location_label="HTMX Test Strike",
            location_lat=Decimal("12.34567890123456"),
            location_lon=Decimal("-98.76543210987654"),
            target="Test Target",
            striker="Test Striker",
        )

    def test_strike_fields_returns_200(self):
        """HTMX endpoint returns 200."""
        response = self.client.get('/submit/strike-fields/')
        self.assertEqual(response.status_code, 200)

    def test_strike_fields_default_existing_type(self):
        """Default strike_type is 'existing'."""
        response = self.client.get('/submit/strike-fields/')
        self.assertEqual(response.context['strike_type'], 'existing')

    def test_strike_fields_with_existing_type(self):
        """Returns strike list fields for 'existing' type."""
        response = self.client.get('/submit/strike-fields/', {'strike_type': 'existing'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['strike_type'], 'existing')
        # Should contain strike_list in the rendered HTML
        self.assertContains(response, 'strike_list')

    def test_strike_fields_with_new_type(self):
        """Returns date fields for 'new' type."""
        response = self.client.get('/submit/strike-fields/', {'strike_type': 'new'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['strike_type'], 'new')
        # Should contain date selection elements
        self.assertContains(response, 'new_strike_date')

    def test_strike_fields_uses_partial_template(self):
        """Endpoint renders partial template."""
        response = self.client.get('/submit/strike-fields/')
        self.assertTemplateUsed(response, 'submit/partials/strike_fields.html')

    def test_strike_fields_context_contains_form(self):
        """Context includes form instance."""
        response = self.client.get('/submit/strike-fields/')
        self.assertIsInstance(response.context['form'], SubmitForm)
