"""
Serializers for events app.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import College, Student, Event, EventRegistration, Attendance, Feedback, AdminUser


class CollegeSerializer(serializers.ModelSerializer):
    """Serializer for College model."""
    
    class Meta:
        model = College
        fields = ['id', 'code', 'name', 'address', 'contact_email', 'contact_phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model."""
    
    college_name = serializers.CharField(source='college.name', read_only=True)
    college_code = serializers.CharField(source='college.code', read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'college', 'college_name', 'college_code',
            'first_name', 'last_name', 'full_name', 'email', 'phone',
            'department', 'year_of_study', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    
    college_name = serializers.CharField(source='college.name', read_only=True)
    college_code = serializers.CharField(source='college.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    current_registrations_count = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'event_code', 'college', 'college_name', 'college_code',
            'title', 'description', 'event_type', 'start_date', 'end_date',
            'location', 'max_participants', 'registration_start_date', 'registration_deadline', 'status',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'current_registrations_count', 'is_registration_open', 'is_full'
        ]
        read_only_fields = ['id', 'event_code', 'created_at', 'updated_at']


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for EventRegistration model."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_code = serializers.CharField(source='event.event_code', read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = [
            'id', 'event', 'student', 'student_name', 'student_email',
            'event_title', 'event_code', 'registration_date', 'status'
        ]
        read_only_fields = ['id', 'registration_date']


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_code = serializers.CharField(source='event.event_code', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.username', read_only=True)
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'event', 'student', 'student_name', 'student_email',
            'event_title', 'event_code', 'check_in_time', 'check_out_time',
            'attendance_status', 'marked_by', 'marked_by_name', 'notes', 'duration'
        ]
        read_only_fields = ['id', 'check_in_time']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_code = serializers.CharField(source='event.event_code', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'event', 'student', 'student_name', 'student_email',
            'event_title', 'event_code', 'rating', 'comments', 'submitted_at'
        ]
        read_only_fields = ['id', 'submitted_at']


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for AdminUser model."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    college_code = serializers.CharField(source='college.code', read_only=True)
    
    class Meta:
        model = AdminUser
        fields = [
            'id', 'college', 'college_name', 'college_code',
            'user', 'username', 'email', 'role', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EventRegistrationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating event registrations."""
    
    class Meta:
        model = EventRegistration
        fields = ['event', 'student']
    
    def validate(self, data):
        """Validate registration data."""
        event = data['event']
        student = data['student']
        
        # Check if registration is open
        if not event.is_registration_open:
            raise serializers.ValidationError("Registration is not open for this event.")
        
        # Check if already registered
        if EventRegistration.objects.filter(event=event, student=student).exists():
            raise serializers.ValidationError("Student is already registered for this event.")
        
        # Check if event is full
        if event.is_full:
            raise serializers.ValidationError("Event is at full capacity.")
        
        return data


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating attendance records."""
    
    class Meta:
        model = Attendance
        fields = ['event', 'student', 'attendance_status', 'notes']
    
    def validate(self, data):
        """Validate attendance data."""
        event = data['event']
        student = data['student']
        
        # Check if student is registered for the event
        if not EventRegistration.objects.filter(event=event, student=student, status='registered').exists():
            raise serializers.ValidationError("Student is not registered for this event.")
        
        # Check if attendance already exists
        if Attendance.objects.filter(event=event, student=student).exists():
            raise serializers.ValidationError("Attendance record already exists for this student.")
        
        return data


class FeedbackCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating feedback records."""
    
    class Meta:
        model = Feedback
        fields = ['event', 'student', 'rating', 'comments']
    
    def validate(self, data):
        """Validate feedback data."""
        event = data['event']
        student = data['student']
        
        # Check if student attended the event
        if not Attendance.objects.filter(event=event, student=student, attendance_status='present').exists():
            raise serializers.ValidationError("Student must have attended the event to provide feedback.")
        
        # Check if feedback already exists
        if Feedback.objects.filter(event=event, student=student).exists():
            raise serializers.ValidationError("Feedback already submitted for this event.")
        
        return data

