import random
from django.core.management.base import BaseCommand
from django.conf import settings
from faker import Faker
from app.models.contact import Contact
from app.models.scam import ScamRecord
from app.models.user import User
from app.models.interaction import Interaction
from app.utils import normalize_phone_number
import os

fake = Faker()


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)'
        )
        parser.add_argument(
            '--max-contacts',
            type=int,
            default=10,
            help='Max contacts per user (default: 10)'
        )
        parser.add_argument(
            '--max-spam',
            type=int,
            default=5,
            help='Max spam reports per user (default: 5)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='password123',
            help='Default password for test users (default: password123)'
        )

    def handle(self, *args, **kwargs):
        num_users = kwargs['users']
        max_contacts = kwargs['max_contacts']
        max_spam = kwargs['max_spam']
        default_password = kwargs['password']
        
        self.stdout.write(self.style.SUCCESS(f'Starting to populate database...'))
        self.stdout.write(f'Creating {num_users} users...')
        
        self.populate_database(num_users, max_contacts, max_spam, default_password)
        
        self.stdout.write(self.style.SUCCESS('✅ Database populated successfully!'))

    def create_sample_user(self, default_password):
        """Create a user with properly hashed password"""
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Get default region from settings
        default_region = getattr(settings, 'PHONENUMBER_DEFAULT_REGION', 'IN')
        
        # Generate phone based on region
        if default_region == 'IN':
            phone_number = f"{random.randint(6000000000, 9999999999)}"
        elif default_region == 'US':
            phone_number = f"{random.randint(2000000000, 9999999999)}"
        else:
            phone_number = f"{random.randint(1000000000, 9999999999)}"
        
        # Generate unique phone number
        while True:
            try:
                normalized_phone = normalize_phone_number(phone_number)
                
                # Check if exists
                if not User.objects.filter(phone_number=normalized_phone).exists():
                    break
            except:
                if default_region == 'IN':
                    phone_number = f"{random.randint(6000000000, 9999999999)}"
                else:
                    phone_number = f"{random.randint(1000000000, 9999999999)}"
                continue
        
        # Random email (50% chance)
        email = fake.email() if random.choice([True, False]) else None
        
        # Create user with password from argument
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=normalized_phone,
            password=default_password,
            email=email
        )
        
        self.stdout.write(f'  Created user: {user.get_full_name()} ({user.phone_number})')
        return user

    def create_sample_contact(self, user):
        """Create a contact for a user"""
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Get default region from settings
        default_region = getattr(settings, 'PHONENUMBER_DEFAULT_REGION', 'IN')
        
        # Generate phone based on region
        if default_region == 'IN':
            phone_number = f"{random.randint(6000000000, 9999999999)}"
        else:
            phone_number = f"{random.randint(1000000000, 9999999999)}"
        
        try:
            normalized_phone = normalize_phone_number(phone_number)
        except:
            return None
        
        try:
            contact = Contact.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone_number=normalized_phone,
                created_by=user,
                updated_by=user
            )
            return contact
        except Exception as e:
            return None

    def create_sample_spam(self, phone_number, user):
        """Create a spam report"""
        try:
            normalized_phone = normalize_phone_number(phone_number)
        except:
            return None
        
        descriptions = [
            'Telemarketing call',
            'Spam message',
            'Scam attempt',
            'Unwanted promotional call',
            'Phishing attempt',
            'Robocall',
            'Fraudulent activity'
        ]
        
        try:
            spam = ScamRecord.objects.create(
                phone_number=normalized_phone,
                reported_by=user,
                created_by=user,
                updated_by=user,
                description=random.choice(descriptions)
            )
            return spam
        except Exception as e:
            return None

    def create_sample_interaction(self, initiator, receiver_phone):
        """Create a random interaction"""
        interaction_type = random.choice(['call', 'message', 'spam_report'])
        
        # Find receiver if they're a registered user
        try:
            normalized_phone = normalize_phone_number(receiver_phone)
            receiver_user = User.objects.filter(phone_number=normalized_phone).first()
        except:
            receiver_user = None
            normalized_phone = receiver_phone
        
        # Create metadata based on type
        metadata = {}
        if interaction_type == 'call':
            metadata = {'duration': random.randint(10, 600)}
        elif interaction_type == 'message':
            metadata = {'message_length': random.randint(10, 200)}
        
        try:
            interaction = Interaction.objects.create(
                initiator=initiator,
                receiver=receiver_user,
                receiver_phone=normalized_phone,
                interaction_type=interaction_type,
                metadata=metadata
            )
            return interaction
        except Exception as e:
            return None

    def populate_database(self, num_users=50, max_contacts_per_user=10, max_spam_per_user=5, default_password='password123'):
        """Main population logic"""
        users = []
        
        # Get default region from settings
        default_region = getattr(settings, 'PHONENUMBER_DEFAULT_REGION', 'IN')

        # Create users
        self.stdout.write(self.style.WARNING('\n📱 Creating Users...'))
        for i in range(num_users):
            user = self.create_sample_user(default_password)
            if user:
                users.append(user)

        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(users)} users'))

        # Create contacts for each user
        self.stdout.write(self.style.WARNING('\n📞 Creating Contacts...'))
        total_contacts = 0
        for user in users:
            num_contacts = random.randint(0, max_contacts_per_user)
            for _ in range(num_contacts):
                contact = self.create_sample_contact(user)
                if contact:
                    total_contacts += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Created {total_contacts} contacts'))

        # Create spam reports
        self.stdout.write(self.style.WARNING('\n🚫 Creating Spam Reports...'))
        total_spam = 0
        all_phone_numbers = [u.phone_number for u in users]
        
        for user in users:
            num_spam = random.randint(0, max_spam_per_user)
            for _ in range(num_spam):
                if random.random() > 0.3 and all_phone_numbers:
                    phone_to_report = random.choice(all_phone_numbers)
                else:
                    if default_region == 'IN':
                        phone_to_report = f"{random.randint(6000000000, 9999999999)}"
                    else:
                        phone_to_report = f"{random.randint(1000000000, 9999999999)}"
                
                spam = self.create_sample_spam(phone_to_report, user)
                if spam:
                    total_spam += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Created {total_spam} spam reports'))

        # Create interactions
        self.stdout.write(self.style.WARNING('\n💬 Creating Interactions...'))
        total_interactions = 0
        
        for user in users:
            num_interactions = random.randint(5, 20)
            for _ in range(num_interactions):
                if random.random() > 0.3 and all_phone_numbers:
                    receiver_phone = random.choice(all_phone_numbers)
                else:
                    if default_region == 'IN':
                        receiver_phone = f"{random.randint(6000000000, 9999999999)}"
                    else:
                        receiver_phone = f"{random.randint(1000000000, 9999999999)}"
                
                interaction = self.create_sample_interaction(user, receiver_phone)
                if interaction:
                    total_interactions += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Created {total_interactions} interactions'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('DATABASE POPULATION SUMMARY:'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'👥 Users: {len(users)}')
        self.stdout.write(f'📞 Contacts: {total_contacts}')
        self.stdout.write(f'🚫 Spam Reports: {total_spam}')
        self.stdout.write(f'💬 Interactions: {total_interactions}')
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.WARNING('\n📝 Test User Credentials:'))
        self.stdout.write(f'   Phone: {users[0].phone_number if users else "N/A"}')
        self.stdout.write(f'   Password: {default_password}')
        self.stdout.write(f'   Region: {default_region}')
        self.stdout.write(self.style.SUCCESS('='*50 + '\n'))