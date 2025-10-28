from django.core.management.base import BaseCommand
from apps.organizations.models import Organization
from apps.warehouses.models import Warehouse
from apps.users.models import User
from apps.customers.models import Customer


class Command(BaseCommand):
    help = 'Seed initial data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Creating seed data...')
        
        # Create Organization
        org, created = Organization.objects.get_or_create(
            organization_id=1,
            defaults={
                'name': 'ZigoPay Logistics Ltd',
                'address': '123 Main Street, Dar es Salaam, Tanzania',
                'contact_phone': '+255123456789',
                'contact_email': 'info@zigopay.com',
                'status': 'active'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created organization'))
        else:
            self.stdout.write('Organization already exists')
        
        # Create Warehouse
        warehouse, created = Warehouse.objects.get_or_create(
            warehouse_id=1,
            defaults={
                'warehouse_name': 'Dar es Salaam Main Warehouse',
                'location': 'Port Area, Dar es Salaam',
                'organization': org,
                'capacity': 1000,
                'status': 'active'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created warehouse'))
        
        # Create Superuser (Admin)
        if not User.objects.filter(username='admin@zigopay.com').exists():
            User.objects.create_superuser(
                username='admin@zigopay.com',
                email='admin@zigopay.com',
                password='admin123',
                full_name='John Admin',
                phone_number='+255123456789',
                role='admin',
                organization=org,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Created admin user'))
            self.stdout.write(self.style.WARNING('  Username: admin@zigopay.com'))
            self.stdout.write(self.style.WARNING('  Password: admin123'))
        else:
            self.stdout.write('Admin user already exists')
        
        # Create Warehouse Manager
        if not User.objects.filter(username='manager@zigopay.com').exists():
            manager = User.objects.create_user(
                username='manager@zigopay.com',
                email='manager@zigopay.com',
                password='manager123',
                full_name='Sarah Manager',
                phone_number='+255123456790',
                role='warehouse_manager',
                organization=org,
                warehouse=warehouse,
                is_active=True
            )
            warehouse.manager = manager
            warehouse.save()
            self.stdout.write(self.style.SUCCESS('✓ Created warehouse manager'))
            self.stdout.write(self.style.WARNING('  Username: manager@zigopay.com'))
            self.stdout.write(self.style.WARNING('  Password: manager123'))
        else:
            self.stdout.write('Warehouse manager already exists')
        
        # Create Officer
        if not User.objects.filter(username='officer@zigopay.com').exists():
            User.objects.create_user(
                username='officer@zigopay.com',
                email='officer@zigopay.com',
                password='officer123',
                full_name='Mike Officer',
                phone_number='+255123456791',
                role='officer',
                organization=org,
                warehouse=warehouse,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Created officer'))
            self.stdout.write(self.style.WARNING('  Username: officer@zigopay.com'))
            self.stdout.write(self.style.WARNING('  Password: officer123'))
        else:
            self.stdout.write('Officer already exists')
        
        # Create Customer
        if not Customer.objects.filter(customer_id=1).exists():
            customer = Customer.objects.create(
                customer_id=1,
                customer_name='ABC Trading Company',
                phone_number='+255712345678',
                email='info@abctrading.com',
                address='Industrial Area, Dar es Salaam',
                preferred_communication='whatsapp',
                organization=org
            )
            self.stdout.write(self.style.SUCCESS('✓ Created customer'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Seed data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nAPI Base URL: http://localhost:8000/api/'))
        self.stdout.write(self.style.SUCCESS('Authentication: http://localhost:8000/api/auth/login/'))

