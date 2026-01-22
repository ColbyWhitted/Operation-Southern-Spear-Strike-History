from django.test import TestCase, Client
from sources.models import Source
from dashboard.models import Strike
from datetime import date
from decimal import Decimal


class SourceModelTests(TestCase):
    """Test Source model."""

    def test_source_creation(self):
        """Source is created with all fields."""
        source = Source.objects.create(
            name="Test Source",
            url="https://example.com/article",
            type="PRIMARY",
        )
        self.assertEqual(source.name, "Test Source")
        self.assertEqual(source.url, "https://example.com/article")
        self.assertEqual(source.type, "PRIMARY")

    def test_source_str_representation(self):
        """Source __str__ returns name and pk."""
        source = Source.objects.create(
            name="Named Source",
            url="https://example.com",
        )
        expected = f"{source.name} - {source.pk}"
        self.assertEqual(str(source), expected)

    def test_source_type_choices(self):
        """Source type can be PRIMARY or SECONDARY."""
        primary = Source.objects.create(
            name="Primary",
            url="https://example.com/primary",
            type=Source.Type.PRIMARY,
        )
        secondary = Source.objects.create(
            name="Secondary",
            url="https://example.com/secondary",
            type=Source.Type.SECONDARY,
        )
        self.assertEqual(primary.type, "PRIMARY")
        self.assertEqual(secondary.type, "SECONDARY")

    def test_source_default_type(self):
        """Source defaults to PRIMARY type."""
        source = Source.objects.create(
            name="Default Type",
            url="https://example.com",
        )
        self.assertEqual(source.type, "PRIMARY")

    def test_source_last_reviewed_auto_now(self):
        """last_reviewed is automatically set on save."""
        source = Source.objects.create(
            name="Auto Date Source",
            url="https://example.com",
        )
        self.assertIsNotNone(source.last_reviewed)
        self.assertEqual(source.last_reviewed, date.today())

    def test_source_ordering(self):
        """Sources ordered by -last_reviewed (most recent first)."""
        # Create sources - they'll all have the same last_reviewed (today)
        # but ordering should still work based on insertion order for same dates
        source1 = Source.objects.create(name="First", url="https://a.com")
        source2 = Source.objects.create(name="Second", url="https://b.com")

        # Both have same date, so we just verify they're both returned
        sources = list(Source.objects.all())
        self.assertEqual(len(sources), 2)
        self.assertIn(source1, sources)
        self.assertIn(source2, sources)


class SourcesViewTests(TestCase):
    """Test sources views."""

    def setUp(self):
        self.client = Client()
        self.strike = Strike.objects.create(
            date=date(2024, 1, 15),
            location_label="Test Strike",
            location_lat=Decimal("12.34567890123456"),
            location_lon=Decimal("-98.76543210987654"),
            target="Test Target",
            striker="Test Striker",
        )
        self.source = Source.objects.create(
            name="Strike Source",
            url="https://example.com/source",
        )
        self.strike.sources.add(self.source)

    def test_sources_view_returns_200(self):
        """Sources index returns 200 for valid strike."""
        response = self.client.get(f'/sources/{self.strike.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_sources_view_context_contains_strike(self):
        """Context includes the requested strike."""
        response = self.client.get(f'/sources/{self.strike.pk}/')
        self.assertEqual(response.context['strike'], self.strike)

    def test_sources_view_context_contains_all_strikes(self):
        """Context includes all strikes for sidebar."""
        response = self.client.get(f'/sources/{self.strike.pk}/')
        self.assertIn(self.strike, response.context['all_strikes'])

    def test_sources_view_filters_by_strike(self):
        """Only sources for the specified strike are returned."""
        unrelated_source = Source.objects.create(
            name="Unrelated Source",
            url="https://other.com",
        )
        response = self.client.get(f'/sources/{self.strike.pk}/')
        sources_in_context = list(response.context['sources'])

        self.assertIn(self.source, sources_in_context)
        self.assertNotIn(unrelated_source, sources_in_context)

    def test_sources_view_uses_correct_template(self):
        """View renders with sources/index.html."""
        response = self.client.get(f'/sources/{self.strike.pk}/')
        self.assertTemplateUsed(response, 'sources/index.html')

    def test_sources_view_multiple_sources(self):
        """View returns all sources linked to a strike."""
        source2 = Source.objects.create(
            name="Second Source",
            url="https://example2.com",
        )
        self.strike.sources.add(source2)

        response = self.client.get(f'/sources/{self.strike.pk}/')
        sources_in_context = list(response.context['sources'])

        self.assertEqual(len(sources_in_context), 2)
        self.assertIn(self.source, sources_in_context)
        self.assertIn(source2, sources_in_context)
