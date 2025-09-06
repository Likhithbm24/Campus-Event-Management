"""
Event management models for the Campus Event Management Platform.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class College(models.Model):
    """Model representing a college/institution."""
    
    code = models.CharField(max_length=10, unique=True, help_text="Unique college code (e.g., 'TECH', 'MED')")
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    """Model representing a student."""
    
    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
        (5, 'Fifth Year'),
    ]
    
    student_id = models.CharField(max_length=20, help_text="College-specific student ID")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='students')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student_id', 'college']
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Event(models.Model):
    """Model representing an event."""
    
    EVENT_TYPE_CHOICES = [
        ('hackathon', 'Hackathon'),
        ('workshop', 'Workshop'),
        ('tech_talk', 'Tech Talk'),
        ('fest', 'Festival'),
        ('seminar', 'Seminar'),
        ('competition', 'Competition'),
        ('conference', 'Conference'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('draft', 'Draft'),
    ]
    
    event_code = models.CharField(max_length=50, unique=True, help_text="Unique event identifier")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    max_participants = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    registration_start_date = models.DateTimeField(null=True, blank=True, help_text="When registration opens")
    registration_deadline = models.DateTimeField(null=True, blank=True, help_text="When registration closes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['college', 'start_date']),
            models.Index(fields=['event_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.event_code} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.event_code:
            self.event_code = self.generate_event_code()
        super().save(*args, **kwargs)
    
    def generate_event_code(self):
        """Generate unique event code in format: {CollegeCode}-{EventType}-{YYYYMMDD}-{Sequence}"""
        from datetime import datetime
        
        date_str = self.start_date.strftime('%Y%m%d')
        event_type_short = self.event_type.upper()[:4]
        
        # Get next sequence number for this college, event type, and date
        existing_events = Event.objects.filter(
            college=self.college,
            event_type=self.event_type,
            start_date__date=self.start_date.date()
        ).count()
        
        sequence = existing_events + 1
        return f"{self.college.code}-{event_type_short}-{date_str}-{sequence:03d}"
    
    @property
    def is_registration_open(self):
        """Check if registration is still open."""
        if self.status != 'active':
            return False
        
        now = timezone.now()
        
        # Check if registration has started
        if self.registration_start_date and now < self.registration_start_date:
            return False
        
        # Check if registration has ended
        if self.registration_deadline:
            return now < self.registration_deadline
        
        # If no registration deadline, registration closes when event starts
        return now < self.start_date
    
    @property
    def current_registrations_count(self):
        """Get current number of registrations."""
        return self.registrations.filter(status='registered').count()
    
    @property
    def is_full(self):
        """Check if event is at capacity."""
        if not self.max_participants:
            return False
        return self.current_registrations_count >= self.max_participants


class EventRegistration(models.Model):
    """Model representing student registration for an event."""
    
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('cancelled', 'Cancelled'),
        ('waitlisted', 'Waitlisted'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    
    class Meta:
        unique_together = ['event', 'student']
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['student']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        # Check if event is full and set status accordingly
        if self.status == 'registered' and self.event.is_full:
            self.status = 'waitlisted'
        super().save(*args, **kwargs)


class Attendance(models.Model):
    """Model representing student attendance at an event."""
    
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    attendance_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['event', 'student']
        ordering = ['-check_in_time']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['student']),
            models.Index(fields=['attendance_status']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.event.title} ({self.attendance_status})"
    
    @property
    def duration(self):
        """Calculate attendance duration."""
        if self.check_out_time:
            return self.check_out_time - self.check_in_time
        return None


class Feedback(models.Model):
    """Model representing student feedback for an event."""
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedback')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (poor) to 5 (excellent)"
    )
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['event', 'student']
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['student']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.event.title} ({self.rating}/5)"


class AdminUser(models.Model):
    """Model representing admin users for colleges."""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='admin_users')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} ({self.college.code})"

