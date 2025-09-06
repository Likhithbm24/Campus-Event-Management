"""
Tests for the Campus Event Management Platform models.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from events.models import College, Student, Event, EventRegistration, Attendance, Feedback


class CollegeModelTest(TestCase):
    """Test cases for College model."""

    def setUp(self):
        self.college = College.objects.create(
            code='TECH',
            name='Tech University',
            address='123 Tech Street',
            contact_email='contact@tech.edu',
            contact_phone='+1-555-0123'
        )

    def test_college_creation(self):
        """Test college creation."""
        self.assertEqual(self.college.code, 'TECH')
        self.assertEqual(self.college.name, 'Tech University')
        self.assertTrue(self.college.created_at)

    def test_college_str_representation(self):
        """Test string representation of college."""
        expected = 'TECH - Tech University'
        self.assertEqual(str(self.college), expected)

    def test_college_code_unique(self):
        """Test that college code must be unique."""
        with self.assertRaises(Exception):
            College.objects.create(
                code='TECH',
                name='Another Tech University'
            )


class StudentModelTest(TestCase):
    """Test cases for Student model."""

    def setUp(self):
        self.college = College.objects.create(
            code='TECH',
            name='Tech University'
        )
        self.student = Student.objects.create(
            student_id='TECH001',
            college=self.college,
            first_name='John',
            last_name='Doe',
            email='john.doe@tech.edu',
            department='Computer Science',
            year_of_study=3
        )

    def test_student_creation(self):
        """Test student creation."""
        self.assertEqual(self.student.student_id, 'TECH001')
        self.assertEqual(self.student.full_name, 'John Doe')
        self.assertEqual(self.student.college, self.college)

    def test_student_str_representation(self):
        """Test string representation of student."""
        expected = 'John Doe (TECH001)'
        self.assertEqual(str(self.student), expected)

    def test_student_email_unique(self):
        """Test that student email must be unique."""
        with self.assertRaises(Exception):
            Student.objects.create(
                student_id='TECH002',
                college=self.college,
                first_name='Jane',
                last_name='Smith',
                email='john.doe@tech.edu'  # Same email
            )


class EventModelTest(TestCase):
    """Test cases for Event model."""

    def setUp(self):
        self.college = College.objects.create(
            code='TECH',
            name='Tech University'
        )
        self.event = Event.objects.create(
            college=self.college,
            title='Tech Conference 2024',
            description='Annual technology conference',
            event_type='conference',
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=31),
            location='Tech Auditorium',
            max_participants=100
        )

    def test_event_creation(self):
        """Test event creation."""
        self.assertEqual(self.event.title, 'Tech Conference 2024')
        self.assertEqual(self.event.event_type, 'conference')
        self.assertTrue(self.event.event_code)  # Should be auto-generated

    def test_event_code_generation(self):
        """Test event code generation."""
        expected_pattern = r'TECH-CONF-\d{8}-\d{3}'
        import re
        self.assertTrue(re.match(expected_pattern, self.event.event_code))

    def test_event_registration_open(self):
        """Test event registration status."""
        # Future event should have open registration
        self.assertTrue(self.event.is_registration_open)

    def test_event_full_status(self):
        """Test event full status."""
        self.assertFalse(self.event.is_full)  # No registrations yet


class EventRegistrationModelTest(TestCase):
    """Test cases for EventRegistration model."""

    def setUp(self):
        self.college = College.objects.create(
            code='TECH',
            name='Tech University'
        )
        self.student = Student.objects.create(
            student_id='TECH001',
            college=self.college,
            first_name='John',
            last_name='Doe',
            email='john.doe@tech.edu'
        )
        self.event = Event.objects.create(
            college=self.college,
            title='Tech Conference 2024',
            event_type='conference',
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=31),
            max_participants=1  # Small limit for testing
        )
        self.registration = EventRegistration.objects.create(
            event=self.event,
            student=self.student
        )

    def test_registration_creation(self):
        """Test event registration creation."""
        self.assertEqual(self.registration.event, self.event)
        self.assertEqual(self.registration.student, self.student)
        self.assertEqual(self.registration.status, 'registered')

    def test_registration_str_representation(self):
        """Test string representation of registration."""
        expected = 'John Doe - Tech Conference 2024'
        self.assertEqual(str(self.registration), expected)

    def test_unique_registration(self):
        """Test that same student cannot register twice for same event."""
        with self.assertRaises(Exception):
            EventRegistration.objects.create(
                event=self.event,
                student=self.student
            )


class AttendanceModelTest(TestCase):
    """Test cases for Attendance model."""

    def setUp(self):
        self.college = College.objects.create(
            code='TECH',
            name='Tech University'
        )
        self.student = Student.objects.create(
            student_id='TECH001',
            college=self.college,
            first_name='John',
            last_name='Doe',
            email='john.doe@tech.edu'
        )
        self.event = Event.objects.create(
            college=self.college,
            title='Tech Conference 2024',
            event_type='conference',
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=31)
        )
        self.attendance = Attendance.objects.create(
            event=self.event,
            student=self.student,
            attendance_status='present'
        )

    def test_attendance_creation(self):
        """Test attendance creation."""
        self.assertEqual(self.attendance.event, self.event)
        self.assertEqual(self.attendance.student, self.student)
        self.assertEqual(self.attendance.attendance_status, 'present')
        self.assertTrue(self.attendance.check_in_time)

    def test_attendance_str_representation(self):
        """Test string representation of attendance."""
        expected = 'John Doe - Tech Conference 2024 (present)'
        self.assertEqual(str(self.attendance), expected)

    def test_unique_attendance(self):
        """Test that same student cannot have multiple attendance records for same event."""
        with self.assertRaises(Exception):
            Attendance.objects.create(
                event=self.event,
                student=self.student,
                attendance_status='present'
            )


class FeedbackModelTest(TestCase):
    """Test cases for Feedback model."""

    def setUp(self):
        self.college = College.objects.create(
            code='TECH',
            name='Tech University'
        )
        self.student = Student.objects.create(
            student_id='TECH001',
            college=self.college,
            first_name='John',
            last_name='Doe',
            email='john.doe@tech.edu'
        )
        self.event = Event.objects.create(
            college=self.college,
            title='Tech Conference 2024',
            event_type='conference',
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=31)
        )
        self.feedback = Feedback.objects.create(
            event=self.event,
            student=self.student,
            rating=5,
            comments='Excellent event!'
        )

    def test_feedback_creation(self):
        """Test feedback creation."""
        self.assertEqual(self.feedback.event, self.event)
        self.assertEqual(self.feedback.student, self.student)
        self.assertEqual(self.feedback.rating, 5)
        self.assertEqual(self.feedback.comments, 'Excellent event!')

    def test_feedback_str_representation(self):
        """Test string representation of feedback."""
        expected = 'John Doe - Tech Conference 2024 (5/5)'
        self.assertEqual(str(self.feedback), expected)

    def test_feedback_rating_validation(self):
        """Test feedback rating validation."""
        # Test rating too high
        with self.assertRaises(ValidationError):
            feedback = Feedback(
                event=self.event,
                student=self.student,
                rating=6,
                comments='Test'
            )
            feedback.full_clean()

        # Test rating too low
        with self.assertRaises(ValidationError):
            feedback = Feedback(
                event=self.event,
                student=self.student,
                rating=0,
                comments='Test'
            )
            feedback.full_clean()

    def test_unique_feedback(self):
        """Test that same student cannot provide multiple feedback for same event."""
        with self.assertRaises(Exception):
            Feedback.objects.create(
                event=self.event,
                student=self.student,
                rating=4,
                comments='Another feedback'
            )

