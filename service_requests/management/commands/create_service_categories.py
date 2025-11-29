from django.core.management.base import BaseCommand
from service_requests.models import ServiceCategory

class Command(BaseCommand):
    help = 'Create default service categories'

    def handle(self, *args, **options):
        categories = [
            'Maid/Cleaning', 'Cook', 'Carpenter', 'Electrician', 'Constructor',
            'Painter', 'Plumber', 'Pharmacy', 'Salon', 'Beauty Parlour',
            'Dry Cleaning', 'Babysitter/Nanny', 'AC Service', 'Pest Control'
        ]

        for i, category_name in enumerate(categories, 1):
            category, created = ServiceCategory.objects.get_or_create(
                id=i,
                defaults={
                    'name': category_name,
                    'slug': category_name.lower().replace(' ', '-').replace('/', '-')
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created all service categories!')
        )