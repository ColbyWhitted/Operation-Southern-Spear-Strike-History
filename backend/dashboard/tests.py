from django.test import TestCase, Client
from dashboard.models import Strike
from sources.models import Source
from decimal import Decimal
from datetime import date


class StrikeModelTests(TestCase):
    """Test Strike model creation and relationships."""

    def setUp(self):
        """Create test data - runs before each test method."""
        self.strike = Strike.objects.create(
            date=date(2024, 1, 15),
            location_label="Test Location",
            location_lat=Decimal("12.34567890123456"),
            location_lon=Decimal("-98.76543210987654"),
            target="Test Target",
            striker="Test Striker",
        )

    def test_strike_creation(self):
        """Strike object is created with correct fields."""
        self.assertEqual(self.strike.location_label, "Test Location")
        self.assertEqual(self.strike.date, date(2024, 1, 15))
        self.assertEqual(self.strike.target, "Test Target")
        self.assertEqual(self.strike.striker, "Test Striker")

    def test_strike_str_representation(self):
        """Strike __str__ returns date and pk."""
        expected = f"{self.strike.date} - {self.strike.pk}"
        self.assertEqual(str(self.strike), expected)

    def test_strike_ordering(self):
        """Strikes are ordered by -date (newest first)."""
        older_strike = Strike.objects.create(
            date=date(2023, 6, 1),
            location_label="Older Strike",
            location_lat=Decimal("10.00000000000000"),
            location_lon=Decimal("-90.00000000000000"),
            target="Old Target",
            striker="Old Striker",
        )
        strikes = list(Strike.objects.all())
        self.assertEqual(strikes[0], self.strike)  # Newer first
        self.assertEqual(strikes[1], older_strike)

    def test_strike_source_relationship(self):
        """Strike can have multiple sources via ManyToMany."""
        source1 = Source.objects.create(name="Source 1", url="https://example.com/1")
        source2 = Source.objects.create(name="Source 2", url="https://example.com/2")
        self.strike.sources.add(source1, source2)

        self.assertEqual(self.strike.sources.count(), 2)
        self.assertIn(source1, self.strike.sources.all())
        self.assertIn(source2, self.strike.sources.all())

    def test_strike_optional_fields(self):
        """Strike can be created with only required fields."""
        minimal_strike = Strike.objects.create(
            date=date(2024, 2, 1),
            location_label="Minimal",
            target="Target",
            striker="Striker",
        )
        self.assertIsNone(minimal_strike.location_lat)
        self.assertIsNone(minimal_strike.location_lon)
        self.assertIsNone(minimal_strike.crew_number)
        self.assertIsNone(minimal_strike.number_killed)
        self.assertIsNone(minimal_strike.image_url)
        self.assertIsNone(minimal_strike.video_url)


class DashboardViewTests(TestCase):
    """Test dashboard views."""

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

    def test_index_view_returns_200(self):
        """Dashboard index returns 200 for valid strike pk."""
        response = self.client.get(f'/dashboard/{self.strike.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_index_view_context_contains_strike(self):
        """Context includes the requested strike."""
        response = self.client.get(f'/dashboard/{self.strike.pk}/')
        self.assertEqual(response.context['strike'], self.strike)

    def test_index_view_context_contains_all_strikes(self):
        """Context includes all strikes for sidebar."""
        second_strike = Strike.objects.create(
            date=date(2024, 2, 1),
            location_label="Second Strike",
            location_lat=Decimal("10.00000000000000"),
            location_lon=Decimal("-90.00000000000000"),
            target="Second Target",
            striker="Second Striker",
        )
        response = self.client.get(f'/dashboard/{self.strike.pk}/')
        all_strikes = list(response.context['all_strikes'])
        self.assertEqual(len(all_strikes), 2)
        self.assertIn(self.strike, all_strikes)
        self.assertIn(second_strike, all_strikes)

    def test_index_view_uses_correct_template(self):
        """View renders with dashboard/index.html."""
        response = self.client.get(f'/dashboard/{self.strike.pk}/')
        self.assertTemplateUsed(response, 'dashboard/index.html')
