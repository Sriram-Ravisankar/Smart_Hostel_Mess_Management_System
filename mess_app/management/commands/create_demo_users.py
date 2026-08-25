from django.core.management.base import BaseCommand
from mess_app.models import User

class Command(BaseCommand):
    help = 'Creates default demo accounts (admin and student) for recruiters and reviewers.'

    def handle(self, *args, **kwargs):
        # 1. Create or update Demo Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@messnet.com',
                'role': User.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Demo',
                'last_name': 'Admin'
            }
        )
        admin_user.set_password('admin123')
        admin_user.role = User.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS('Created demo admin user: admin / admin123'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated demo admin user password to: admin123'))

        # 2. Create or update Demo Student
        student_user, created = User.objects.get_or_create(
            username='student',
            defaults={
                'email': 'student@messnet.com',
                'role': User.STUDENT,
                'department': 'Computer Science',
                'mobile_number': '+919876543210',
                'first_name': 'Demo',
                'last_name': 'Student'
            }
        )
        student_user.set_password('student123')
        student_user.role = User.STUDENT
        student_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS('Created demo student user: student / student123'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated demo student user password to: student123'))
