from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from accounts.models import CustomUser
from workspaces.models import Amenity, CoWorkingSpace, WorkspaceUnit
from bookings.models import Booking
from bookings.views import check_availability_logic

class CoWorkPlatformTests(TestCase):
    def setUp(self):
        # Create users
        self.owner = CustomUser.objects.create_user(
            username="owner_test",
            email="owner@test.com",
            password="testpassword",
            role="OWNER"
        )
        self.client_user = CustomUser.objects.create_user(
            username="client_test",
            email="client@test.com",
            password="testpassword",
            role="CLIENT"
        )
        
        # Create a workspace space
        self.space = CoWorkingSpace.objects.create(
            owner=self.owner,
            name="Test Space Studio",
            description="Studio co-working space",
            address="456 Tech Way",
            city="TechCity"
        )
        
        # Create units
        self.desk = WorkspaceUnit.objects.create(
            space=self.space,
            name="Hot Desk 1",
            type="DESK",
            seating_capacity=1,
            area_sqft=15,
            price_per_day=20
        )
        self.cabin = WorkspaceUnit.objects.create(
            space=self.space,
            name="Cabin Suite",
            type="CABIN",
            seating_capacity=6,
            area_sqft=120,
            price_per_day=80
        )

    def test_user_roles(self):
        """Test user role verification helpers"""
        self.assertTrue(self.client_user.is_client())
        self.assertFalse(self.client_user.is_owner())
        self.assertTrue(self.owner.is_owner())
        self.assertFalse(self.owner.is_client())

    def test_availability_logic(self):
        """Test that overlapping booking requests are correctly identified and rejected"""
        today = datetime.today().date()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        # Initial booking
        Booking.objects.create(
            user=self.client_user,
            unit=self.desk,
            start_date=today,
            end_date=tomorrow,
            total_price=40.00,
            status='APPROVED'
        )
        
        # Check conflict overlapping dates
        is_available = check_availability_logic(self.desk, today, tomorrow)
        self.assertFalse(is_available, "Dates overlap completely with approved booking")
        
        # Check conflict partial overlap
        is_available = check_availability_logic(self.desk, tomorrow, next_week)
        self.assertFalse(is_available, "Dates overlap at tomorrow limit")
        
        # Check non-conflicting dates
        future_start = today + timedelta(days=3)
        future_end = today + timedelta(days=5)
        is_available = check_availability_logic(self.desk, future_start, future_end)
        self.assertTrue(is_available, "Dates in the future with no overlapping bookings should be available")

    def test_search_capacity_filter(self):
        """Test search views capacity filters filter out spaces with insufficient seat sizes"""
        # Search spaces for capacity 1 - both should match
        response = self.client.get(reverse('space_list'), {'capacity': '1'})
        self.assertContains(response, "Test Space Studio")
        
        # Search spaces for capacity 6 - both should match (since cabin capacity is 6)
        response = self.client.get(reverse('space_list'), {'capacity': '6'})
        self.assertContains(response, "Test Space Studio")

        # Search spaces for capacity 10 - no spaces should match (since max capacity is 6)
        response = self.client.get(reverse('space_list'), {'capacity': '10'})
        self.assertNotContains(response, "Test Space Studio")
