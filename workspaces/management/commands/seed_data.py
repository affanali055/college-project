from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from workspaces.models import Amenity, CoWorkingSpace, WorkspaceUnit

class Command(BaseCommand):
    help = "Seeds sample data for co-working spaces platform (amenities, users, spaces, units)."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # 1. Create Amenities
        amenity_data = [
            ("High-Speed Wi-Fi", "wifi"),
            ("Conference Meeting Rooms", "handshake"),
            ("Reserved Parking Lot", "square-parking"),
            ("24/7 Power Backup", "lightbulb"),
            ("Cafeteria & Lounge", "mug-hot"),
            ("Security Surveillance", "shield-halved")
        ]
        
        amenities = {}
        for name, icon in amenity_data:
            amenity, created = Amenity.objects.get_or_create(
                name=name,
                defaults={'icon_class': icon}
            )
            amenities[name] = amenity
            if created:
                self.stdout.write(f"Created Amenity: {name}")

        # 2. Create Sample Users
        # Admin Superuser
        admin_user, created = CustomUser.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@coworkplatform.com",
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True
            }
        )
        if created:
            admin_user.set_password("AdminPass123!")
            admin_user.save()
            self.stdout.write("Created Superuser account: admin / AdminPass123!")

        # Space Owners
        owner_user, created = CustomUser.objects.get_or_create(
            username="owner_john",
            defaults={
                "email": "john@owner.com",
                "role": "OWNER",
                "phone": "+1987654321",
                "company_name": "Executive Spaces Inc"
            }
        )
        if created:
            owner_user.set_password("OwnerPass123!")
            owner_user.save()
            self.stdout.write("Created Space Owner account: owner_john / OwnerPass123!")

        owner_sarah, created = CustomUser.objects.get_or_create(
            username="owner_sarah",
            defaults={
                "email": "sarah@owner.com",
                "role": "OWNER",
                "phone": "+1222333444",
                "company_name": "Skyline Premium Offices"
            }
        )
        if created:
            owner_sarah.set_password("SarahPass123!")
            owner_sarah.save()
            self.stdout.write("Created Space Owner account: owner_sarah / SarahPass123!")

        # Client Users
        client_user, created = CustomUser.objects.get_or_create(
            username="client_alice",
            defaults={
                "email": "alice@client.com",
                "role": "CLIENT",
                "phone": "+1234567890",
                "company_name": "TechStart LLC"
            }
        )
        if created:
            client_user.set_password("ClientPass123!")
            client_user.save()
            self.stdout.write("Created Client account: client_alice / ClientPass123!")

        client_bob, created = CustomUser.objects.get_or_create(
            username="client_bob",
            defaults={
                "email": "bob@client.com",
                "role": "CLIENT",
                "phone": "+1999888777",
                "company_name": "Freelance Devs"
            }
        )
        if created:
            client_bob.set_password("BobPass123!")
            client_bob.save()
            self.stdout.write("Created Client account: client_bob / BobPass123!")

        # 3. Create Sample Spaces & Workspace Units
        # Space 1: Seattle
        space1, created = CoWorkingSpace.objects.get_or_create(
            name="Greenfield Co-Working Oasis",
            defaults={
                "owner": owner_user,
                "description": "A quiet, green, and productivity-focused co-working space located in the heart of Seattle. Excellent natural lighting and full amenities.",
                "address": "1208 Pine St, Suite A",
                "city": "Seattle",
                "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=600&q=80"
            }
        )
        if created:
            space1.amenities.add(
                amenities["High-Speed Wi-Fi"],
                amenities["Reserved Parking Lot"],
                amenities["Cafeteria & Lounge"],
                amenities["24/7 Power Backup"]
            )
            
            # Workspace Units
            WorkspaceUnit.objects.create(
                space=space1,
                name="Dedicated Window Desk A1",
                type="DESK",
                seating_capacity=1,
                area_sqft=15.00,
                price_per_day=20.00
            )
            WorkspaceUnit.objects.create(
                space=space1,
                name="Private Executive Cabin 4B",
                type="CABIN",
                seating_capacity=8,
                area_sqft=180.00,
                price_per_day=110.00
            )
            WorkspaceUnit.objects.create(
                space=space1,
                name="Apex Boardroom 1",
                type="MEETING",
                seating_capacity=12,
                area_sqft=320.00,
                price_per_day=75.00
            )
            self.stdout.write("Created Space: Greenfield Co-Working Oasis (Seattle)")

        # Space 2: Boston
        space2, created = CoWorkingSpace.objects.get_or_create(
            name="Apex Highrise Workspaces",
            defaults={
                "owner": owner_user,
                "description": "Skyline views and premium business setups. Perfect for startup teams and clients visiting Boston. Fully secure and high-speed infrastructure.",
                "address": "500 Boylston St, Floor 14",
                "city": "Boston",
                "image_url": "https://images.unsplash.com/photo-1527192491265-7e15c55b1ed2?auto=format&fit=crop&w=600&q=80"
            }
        )
        if created:
            space2.amenities.add(
                amenities["High-Speed Wi-Fi"],
                amenities["Conference Meeting Rooms"],
                amenities["24/7 Power Backup"],
                amenities["Security Surveillance"]
            )
            
            # Workspace Units
            WorkspaceUnit.objects.create(
                space=space2,
                name="Hot Desk Area B",
                type="DESK",
                seating_capacity=1,
                area_sqft=18.00,
                price_per_day=25.00
            )
            WorkspaceUnit.objects.create(
                space=space2,
                name="Highrise Corner Cabin C3",
                type="CABIN",
                seating_capacity=4,
                area_sqft=110.00,
                price_per_day=90.00
            )
            self.stdout.write("Created Space: Apex Highrise Workspaces (Boston)")

        # Space 3: San Jose
        space3, created = CoWorkingSpace.objects.get_or_create(
            name="Silicon Valley Launchpad",
            defaults={
                "owner": owner_user,
                "description": "Tech hub co-working space offering dynamic team cabins, collaborative meeting rooms, and access to a vibrant community of startup founders.",
                "address": "303 Almaden Blvd",
                "city": "San Jose",
                "image_url": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=600&q=80"
            }
        )
        if created:
            space3.amenities.add(
                amenities["High-Speed Wi-Fi"],
                amenities["Conference Meeting Rooms"],
                amenities["Cafeteria & Lounge"],
                amenities["24/7 Power Backup"],
                amenities["Security Surveillance"]
            )
            
            # Workspace Units
            WorkspaceUnit.objects.create(
                space=space3,
                name="Founder's Suite Cabin 1",
                type="CABIN",
                seating_capacity=10,
                area_sqft=240.00,
                price_per_day=150.00
            )
            self.stdout.write("Created Space: Silicon Valley Launchpad (San Jose)")

        # Space 4: New York
        space4, created = CoWorkingSpace.objects.get_or_create(
            name="Manhattan Skyline Executive Suite",
            defaults={
                "owner": owner_sarah,
                "description": "Located in Midtown Manhattan, this premium space offers private office suites, a corporate meeting space, and breathtaking city skyline views.",
                "address": "230 Park Ave, Floor 25",
                "city": "New York",
                "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=600&q=80"
            }
        )
        if created:
            space4.amenities.add(
                amenities["High-Speed Wi-Fi"],
                amenities["Conference Meeting Rooms"],
                amenities["Cafeteria & Lounge"],
                amenities["24/7 Power Backup"],
                amenities["Security Surveillance"]
            )
            WorkspaceUnit.objects.create(
                space=space4,
                name="Executive Suite A",
                type="CABIN",
                seating_capacity=6,
                area_sqft=150.00,
                price_per_day=180.00
            )
            WorkspaceUnit.objects.create(
                space=space4,
                name="Skyline Boardroom",
                type="MEETING",
                seating_capacity=20,
                area_sqft=450.00,
                price_per_day=120.00
            )
            WorkspaceUnit.objects.create(
                space=space4,
                name="Hot Desk New York",
                type="DESK",
                seating_capacity=1,
                area_sqft=20.00,
                price_per_day=35.00
            )
            self.stdout.write("Created Space: Manhattan Skyline Executive Suite (New York)")

        # Space 5: Austin
        space5, created = CoWorkingSpace.objects.get_or_create(
            name="Austin Creative Garage",
            defaults={
                "owner": owner_user,
                "description": "A relaxed, open-plan workspace designed for freelancers, artists, and creators. Dog-friendly with local coffee on tap.",
                "address": "501 Congress Ave",
                "city": "Austin",
                "image_url": "https://images.unsplash.com/photo-1527192491265-7e15c55b1ed2?auto=format&fit=crop&w=600&q=80"
            }
        )
        if created:
            space5.amenities.add(
                amenities["High-Speed Wi-Fi"],
                amenities["Reserved Parking Lot"],
                amenities["Cafeteria & Lounge"]
            )
            WorkspaceUnit.objects.create(
                space=space5,
                name="Shared Bench Desk 1",
                type="DESK",
                seating_capacity=1,
                area_sqft=16.00,
                price_per_day=15.00
            )
            WorkspaceUnit.objects.create(
                space=space5,
                name="Podcast & Media Studio",
                type="MEETING",
                seating_capacity=4,
                area_sqft=80.00,
                price_per_day=50.00
            )
            self.stdout.write("Created Space: Austin Creative Garage (Austin)")

        # Space 6: Chicago
        space6, created = CoWorkingSpace.objects.get_or_create(
            name="Chicago Loop Workspace",
            defaults={
                "owner": owner_sarah,
                "description": "Professional hybrid office setups right in the Chicago Loop. Perfect for corporate teams needing temporary headquarters.",
                "address": "111 W Jackson Blvd",
                "city": "Chicago",
                "image_url": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=600&q=80"
            }
        )
        if created:
            space6.amenities.add(
                amenities["High-Speed Wi-Fi"],
                amenities["Conference Meeting Rooms"],
                amenities["24/7 Power Backup"],
                amenities["Security Surveillance"]
            )
            WorkspaceUnit.objects.create(
                space=space6,
                name="Team Office Suite 10",
                type="CABIN",
                seating_capacity=15,
                area_sqft=350.00,
                price_per_day=250.00
            )
            WorkspaceUnit.objects.create(
                space=space6,
                name="Hot Desk Chicago",
                type="DESK",
                seating_capacity=1,
                area_sqft=15.00,
                price_per_day=22.00
            )
            self.stdout.write("Created Space: Chicago Loop Workspace (Chicago)")

        # 4. Seed Promo Codes, Reviews, Notifications
        from bookings.models import PromoCode
        from workspaces.models import Review
        from accounts.models import Notification

        PromoCode.objects.get_or_create(code="COWORK10", defaults={"discount_percent": 10})
        PromoCode.objects.get_or_create(code="WELCOME20", defaults={"discount_percent": 20})
        PromoCode.objects.get_or_create(code="SAVEMORE", defaults={"discount_percent": 15})
        PromoCode.objects.get_or_create(code="FESTIVE30", defaults={"discount_percent": 30})
        self.stdout.write("Created Promo Codes: COWORK10, WELCOME20, SAVEMORE, FESTIVE30")

        if not Review.objects.exists():
            Review.objects.create(
                space=space1,
                user=client_user,
                rating=5,
                comment="Absolutely amazing workspace! The Wi-Fi is super fast and John is very accommodating."
            )
            Review.objects.create(
                space=space2,
                user=client_user,
                rating=4,
                comment="Great city view, although parking was a bit tight. Clean and quiet."
            )
            Review.objects.create(
                space=space3,
                user=client_bob,
                rating=5,
                comment="Awesome startup atmosphere. Highly recommended for remote founders!"
            )
            Review.objects.create(
                space=space4,
                user=client_bob,
                rating=5,
                comment="The views from the 25th floor are stunning. Clean desk and quiet boardroom."
            )
            Review.objects.create(
                space=space5,
                user=client_user,
                rating=4,
                comment="Love the community and free local coffee. Dog friendly too!"
            )
            self.stdout.write("Seeded sample reviews.")

        if not Notification.objects.exists():
            Notification.objects.create(
                user=client_user,
                title="Welcome to CoWork!",
                message="Discover local workspaces, check expectations matching and book instantly.",
            )
            Notification.objects.create(
                user=client_bob,
                title="Welcome to CoWork!",
                message="Discover local workspaces, check expectations matching and book instantly.",
            )
            Notification.objects.create(
                user=owner_user,
                title="New Space Registered",
                message="You have successfully registered your properties. Add workspace units to begin receiving bookings.",
            )
            Notification.objects.create(
                user=owner_sarah,
                title="Partner Account Approved",
                message="Welcome to the CoWork network! You can now manage properties and view client expectations.",
            )
            self.stdout.write("Seeded sample notifications.")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))

