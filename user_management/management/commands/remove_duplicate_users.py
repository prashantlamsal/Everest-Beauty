from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Count


class Command(BaseCommand):
    help = 'Remove duplicate user accounts with the same email'

    def handle(self, *args, **options):
        # Find emails with duplicates
        duplicate_emails = (
            User.objects.values('email')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        if not duplicate_emails:
            self.stdout.write(self.style.SUCCESS('No duplicate emails found.'))
            return

        total_deleted = 0
        for entry in duplicate_emails:
            email = entry['email']
            count = entry['count']
            
            # Get all users with this email, ordered by id
            users = list(User.objects.filter(email=email).order_by('id'))
            
            self.stdout.write(f'\nFound {count} users with email: {email}')
            self.stdout.write(f'Keeping user ID {users[0].id} (username: {users[0].username})')
            
            # Delete all except the first one
            for user in users[1:]:
                self.stdout.write(f'  Deleting user ID {user.id} (username: {user.username})')
                user.delete()
                total_deleted += 1

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully deleted {total_deleted} duplicate user(s).')
        )
