"""
Management command to create sample data for testing and development.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from events.models import College, Student, Event, EventRegistration, Attendance, Feedback, AdminUser


class Command(BaseCommand):
    help = 'Create sample data for the Campus Event Management Platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--colleges',
            type=int,
            default=5,
            help='Number of colleges to create'
        )
        parser.add_argument(
            '--students-per-college',
            type=int,
            default=100,
            help='Number of students per college'
        )
        parser.add_argument(
            '--events-per-college',
            type=int,
            default=20,
            help='Number of events per college'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Feedback.objects.all().delete()
        Attendance.objects.all().delete()
        EventRegistration.objects.all().delete()
        Event.objects.all().delete()
        Student.objects.all().delete()
        College.objects.all().delete()
        
        # Create colleges
        colleges = self.create_colleges(options['colleges'])
        
        # Create students
        students = self.create_students(colleges, options['students_per_college'])
        
        # Create events
        events = self.create_events(colleges, options['events_per_college'])
        
        # Create registrations
        self.create_registrations(events, students)
        
        # Create attendance records
        self.create_attendance_records(events, students)
        
        # Create feedback
        self.create_feedback_records(events, students)
        
        # Create admin users
        self.create_admin_users(colleges)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(colleges)} colleges\n'
                f'- {len(students)} students\n'
                f'- {len(events)} events\n'
                f'- Admin users for each college'
            )
        )

    def create_colleges(self, count):
        """Create sample colleges."""
        colleges = []
        college_data = [
            {'code': 'TECH', 'name': 'Tech University', 'department': 'Computer Science'},
            {'code': 'MED', 'name': 'Medical College', 'department': 'Medicine'},
            {'code': 'ENG', 'name': 'Engineering Institute', 'department': 'Engineering'},
            {'code': 'BUS', 'name': 'Business School', 'department': 'Business'},
            {'code': 'ART', 'name': 'Arts College', 'department': 'Fine Arts'},
        ]
        
        for i in range(count):
            data = college_data[i % len(college_data)]
            college = College.objects.create(
                code=data['code'],
                name=data['name'],
                address=f"123 {data['name']} Street, City {i+1}",
                contact_email=f"contact@{data['code'].lower()}.edu",
                contact_phone=f"+1-555-{1000+i:04d}"
            )
            colleges.append(college)
        
        return colleges

    def create_students(self, colleges, students_per_college):
        """Create sample students."""
        students = []
        departments = ['Computer Science', 'Engineering', 'Medicine', 'Business', 'Arts', 'Science', 'Mathematics']
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'James', 'Maria']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        for college in colleges:
            for i in range(students_per_college):
                student = Student.objects.create(
                    student_id=f"{college.code}{i+1:04d}",
                    college=college,
                    first_name=random.choice(first_names),
                    last_name=random.choice(last_names),
                    email=f"student{i+1}@{college.code.lower()}.edu",
                    phone=f"+1-555-{2000+i:04d}",
                    department=random.choice(departments),
                    year_of_study=random.randint(1, 5)
                )
                students.append(student)
        
        return students

    def create_events(self, colleges, events_per_college):
        """Create sample events."""
        events = []
        event_types = ['hackathon', 'workshop', 'tech_talk', 'fest', 'seminar', 'competition', 'conference']
        event_titles = [
            'Annual Tech Conference', 'Machine Learning Workshop', 'Coding Bootcamp',
            'Innovation Hackathon', 'Data Science Seminar', 'Web Development Workshop',
            'AI Research Talk', 'Startup Pitch Competition', 'Tech Career Fair',
            'Cybersecurity Workshop', 'Mobile App Development', 'Cloud Computing Seminar'
        ]
        
        for college in colleges:
            for i in range(events_per_college):
                start_date = timezone.now() + timedelta(days=random.randint(-30, 90))
                end_date = start_date + timedelta(hours=random.randint(2, 8))
                
                event = Event.objects.create(
                    college=college,
                    title=f"{random.choice(event_titles)} {i+1}",
                    description=f"Description for {random.choice(event_titles)} {i+1} at {college.name}",
                    event_type=random.choice(event_types),
                    start_date=start_date,
                    end_date=end_date,
                    location=f"{college.name} Auditorium {i+1}",
                    max_participants=random.randint(50, 500),
                    registration_deadline=start_date - timedelta(days=random.randint(1, 7)),
                    status=random.choice(['active', 'completed', 'cancelled'])
                )
                events.append(event)
        
        return events

    def create_registrations(self, events, students):
        """Create sample event registrations."""
        for event in events:
            # Randomly select students to register
            num_registrations = random.randint(10, min(50, len(students)))
            selected_students = random.sample(students, num_registrations)
            
            for student in selected_students:
                EventRegistration.objects.create(
                    event=event,
                    student=student,
                    status=random.choice(['registered', 'cancelled', 'waitlisted'])
                )

    def create_attendance_records(self, events, students):
        """Create sample attendance records."""
        for event in events:
            # Get registered students for this event
            registered_students = Student.objects.filter(
                registrations__event=event,
                registrations__status='registered'
            )
            
            # Randomly select students who attended
            if len(registered_students) == 0:
                continue
            min_attendance = min(5, len(registered_students))
            num_attendance = random.randint(min_attendance, len(registered_students))
            attended_students = random.sample(list(registered_students), num_attendance)
            
            for student in attended_students:
                check_in_time = event.start_date + timedelta(minutes=random.randint(-30, 30))
                check_out_time = check_in_time + timedelta(hours=random.randint(1, 4))
                
                Attendance.objects.create(
                    event=event,
                    student=student,
                    check_in_time=check_in_time,
                    check_out_time=check_out_time,
                    attendance_status=random.choice(['present', 'late'])
                )

    def create_feedback_records(self, events, students):
        """Create sample feedback records."""
        for event in events:
            # Get students who attended this event
            attended_students = Student.objects.filter(
                attendance__event=event,
                attendance__attendance_status='present'
            )
            
            # Randomly select students who provided feedback
            if len(attended_students) == 0:
                continue
            min_feedback = min(3, len(attended_students))
            num_feedback = random.randint(min_feedback, len(attended_students))
            feedback_students = random.sample(list(attended_students), num_feedback)
            
            for student in feedback_students:
                Feedback.objects.create(
                    event=event,
                    student=student,
                    rating=random.randint(1, 5),
                    comments=f"Great event! Learned a lot about {event.event_type}."
                )

    def create_admin_users(self, colleges):
        """Create admin users for each college."""
        for college in colleges:
            username = f"admin_{college.code.lower()}"
            email = f"admin@{college.code.lower()}.edu"
            
            # Create user if doesn't exist
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': 'Admin',
                    'last_name': college.name,
                    'is_staff': True,
                    'is_superuser': False
                }
            )
            
            if created:
                user.set_password('admin123')
                user.save()
            
            # Create admin user record
            AdminUser.objects.get_or_create(
                college=college,
                user=user,
                defaults={
                    'role': 'admin',
                    'is_active': True
                }
            )
