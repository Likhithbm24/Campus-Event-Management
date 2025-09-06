"""
Student-specific views for the Campus Event Management Platform.
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Count, Avg, Q

from events.models import Student, Event, EventRegistration, Attendance, Feedback
from events.serializers import StudentSerializer


class StudentListView(generics.ListAPIView):
    """List all students with filtering and search capabilities."""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'department', 'year_of_study']
    search_fields = ['first_name', 'last_name', 'email', 'student_id']
    ordering_fields = ['last_name', 'first_name', 'created_at']
    ordering = ['last_name', 'first_name']


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a student."""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_profile(request, student_id):
    """Get comprehensive student profile with statistics."""
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Calculate student statistics
    total_registrations = EventRegistration.objects.filter(
        student=student, status='registered'
    ).count()
    
    total_attendance = Attendance.objects.filter(
        student=student, attendance_status='present'
    ).count()
    
    attendance_rate = 0
    if total_registrations > 0:
        attendance_rate = (total_attendance / total_registrations) * 100
    
    total_feedback = Feedback.objects.filter(student=student).count()
    avg_rating_given = Feedback.objects.filter(student=student).aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0
    
    # Get recent activity
    recent_registrations = EventRegistration.objects.filter(
        student=student, status='registered'
    ).order_by('-registration_date')[:5]
    
    recent_attendance = Attendance.objects.filter(
        student=student, attendance_status='present'
    ).order_by('-check_in_time')[:5]
    
    recent_feedback = Feedback.objects.filter(
        student=student
    ).order_by('-submitted_at')[:5]
    
    # Get event type preferences
    event_type_preferences = EventRegistration.objects.filter(
        student=student, status='registered'
    ).values('event__event_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return Response({
        'student': StudentSerializer(student).data,
        'statistics': {
            'total_registrations': total_registrations,
            'total_attendance': total_attendance,
            'attendance_rate': round(attendance_rate, 2),
            'total_feedback': total_feedback,
            'avg_rating_given': round(avg_rating_given, 2)
        },
        'recent_activity': {
            'registrations': [
                {
                    'event_id': reg.event.id,
                    'event_title': reg.event.title,
                    'event_code': reg.event.event_code,
                    'registration_date': reg.registration_date,
                    'status': reg.status
                }
                for reg in recent_registrations
            ],
            'attendance': [
                {
                    'event_id': att.event.id,
                    'event_title': att.event.title,
                    'event_code': att.event.event_code,
                    'check_in_time': att.check_in_time,
                    'attendance_status': att.attendance_status
                }
                for att in recent_attendance
            ],
            'feedback': [
                {
                    'event_id': fb.event.id,
                    'event_title': fb.event.title,
                    'event_code': fb.event.event_code,
                    'rating': fb.rating,
                    'submitted_at': fb.submitted_at
                }
                for fb in recent_feedback
            ]
        },
        'event_type_preferences': list(event_type_preferences)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_events(request, student_id):
    """Get all events for a specific student with detailed information."""
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get all registrations for the student
    registrations = EventRegistration.objects.filter(student=student).order_by('-registration_date')
    
    # Get additional information for each registration
    events_data = []
    for registration in registrations:
        event = registration.event
        
        # Check if student attended
        attendance = Attendance.objects.filter(
            event=event, student=student
        ).first()
        
        # Check if student provided feedback
        feedback = Feedback.objects.filter(
            event=event, student=student
        ).first()
        
        events_data.append({
            'registration_id': registration.id,
            'event_id': event.id,
            'event_code': event.event_code,
            'title': event.title,
            'description': event.description,
            'event_type': event.event_type,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'location': event.location,
            'college': event.college.name,
            'registration_date': registration.registration_date,
            'registration_status': registration.status,
            'attendance': {
                'checked_in': attendance is not None,
                'check_in_time': attendance.check_in_time if attendance else None,
                'check_out_time': attendance.check_out_time if attendance else None,
                'attendance_status': attendance.attendance_status if attendance else None,
                'notes': attendance.notes if attendance else None
            },
            'feedback': {
                'submitted': feedback is not None,
                'rating': feedback.rating if feedback else None,
                'comments': feedback.comments if feedback else None,
                'submitted_at': feedback.submitted_at if feedback else None
            }
        })
    
    return Response({
        'student_id': student.id,
        'student_name': student.full_name,
        'total_events': len(events_data),
        'events': events_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_attendance(request, student_id):
    """Get attendance history for a specific student."""
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get all attendance records for the student
    attendance_records = Attendance.objects.filter(student=student).order_by('-check_in_time')
    
    # Calculate attendance statistics
    total_attendance = attendance_records.count()
    present_count = attendance_records.filter(attendance_status='present').count()
    late_count = attendance_records.filter(attendance_status='late').count()
    absent_count = attendance_records.filter(attendance_status='absent').count()
    
    # Get attendance by event type
    attendance_by_type = attendance_records.values('event__event_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get attendance by college
    attendance_by_college = attendance_records.values('event__college__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Format attendance records
    attendance_data = []
    for record in attendance_records:
        duration = None
        if record.check_out_time:
            duration = (record.check_out_time - record.check_in_time).total_seconds() / 3600  # hours
        
        attendance_data.append({
            'attendance_id': record.id,
            'event_id': record.event.id,
            'event_code': record.event.event_code,
            'event_title': record.event.title,
            'event_type': record.event.event_type,
            'college': record.event.college.name,
            'check_in_time': record.check_in_time,
            'check_out_time': record.check_out_time,
            'attendance_status': record.attendance_status,
            'duration_hours': round(duration, 2) if duration else None,
            'notes': record.notes,
            'marked_by': record.marked_by.username if record.marked_by else None
        })
    
    return Response({
        'student_id': student.id,
        'student_name': student.full_name,
        'statistics': {
            'total_attendance': total_attendance,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count
        },
        'attendance_by_event_type': list(attendance_by_type),
        'attendance_by_college': list(attendance_by_college),
        'attendance_records': attendance_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_feedback(request, student_id):
    """Get feedback history for a specific student."""
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get all feedback records for the student
    feedback_records = Feedback.objects.filter(student=student).order_by('-submitted_at')
    
    # Calculate feedback statistics
    total_feedback = feedback_records.count()
    avg_rating = feedback_records.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Get rating distribution
    rating_distribution = feedback_records.values('rating').annotate(
        count=Count('id')
    ).order_by('rating')
    
    # Get feedback by event type
    feedback_by_type = feedback_records.values('event__event_type').annotate(
        count=Count('id'),
        avg_rating=Avg('rating')
    ).order_by('-count')
    
    # Format feedback records
    feedback_data = []
    for record in feedback_records:
        feedback_data.append({
            'feedback_id': record.id,
            'event_id': record.event.id,
            'event_code': record.event.event_code,
            'event_title': record.event.title,
            'event_type': record.event.event_type,
            'college': record.event.college.name,
            'rating': record.rating,
            'comments': record.comments,
            'submitted_at': record.submitted_at
        })
    
    return Response({
        'student_id': student.id,
        'student_name': student.full_name,
        'statistics': {
            'total_feedback': total_feedback,
            'avg_rating': round(avg_rating, 2)
        },
        'rating_distribution': list(rating_distribution),
        'feedback_by_event_type': list(feedback_by_type),
        'feedback_records': feedback_data
    })

