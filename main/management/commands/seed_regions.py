from django.core.management.base import BaseCommand
from main.models import Region

class Command(BaseCommand):
    """
    Seed regions into the database
    Creates the initial 5 regions given in the project brief for demonstration purposes
    """

    def handle(self, *args, **kwargs):
        # Check if regions already exist to avoid duplicates
        if Region.objects.exists():
            self.stdout.write(self.style.WARNING('Regions already exist, skipping seeding'))
            return
            
        # Define initial regions
        regions = [
            {
                'name': 'McLaren Vale, South Australia',
                'latitude': -35.22,
                'longitude': 138.54,
            },
            {
                'name': 'Margaret River, Western Australia',
                'latitude': -33.96,
                'longitude': 115.08,
            },
            {
                'name': 'Mornington, Victoria',
                'latitude': -38.22,
                'longitude': 145.04,
            },
            {
                'name': 'Coonawarra, South Australia',
                'latitude': -37.29,
                'longitude': 140.83,
            },
            {
                'name': 'Yarra Valley, Victoria',
                'latitude': -37.75,
                'longitude': 145.10,
            },
        ]
        
        # Create regions
        for region_data in regions:
            Region.objects.create(**region_data)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(regions)} regions'))