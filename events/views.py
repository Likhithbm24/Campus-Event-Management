"""
Views for events app.
"""

from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from .models import College, Student, Event, EventRegistration, Attendance, Feedback, AdminUser
from .serializers import (
    CollegeSerializer, StudentSerializer, EventSerializer,
    EventRegistrationSerializer, AttendanceSerializer, FeedbackSerializer,
    EventRegistrationCreateSerializer, AttendanceCreateSerializer, FeedbackCreateSerializer
)


class CollegeListCreateView(generics.ListCreateAPIView):
    """List and create colleges."""
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CollegeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a college."""
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class StudentListCreateView(generics.ListCreateAPIView):
    """List and create students."""
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


class EventListCreateView(generics.ListCreateAPIView):
    """List and create events."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'event_type', 'status']
    search_fields = ['title', 'description', 'event_code']
    ordering_fields = ['start_date', 'title', 'created_at']
    ordering = ['-start_date']
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an event."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]


class EventRegistrationListCreateView(generics.ListCreateAPIView):
    """List and create event registrations."""
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'student', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'event__title']
    ordering_fields = ['registration_date']
    ordering = ['-registration_date']
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return EventRegistrationCreateSerializer
        return EventRegistrationSerializer


class EventRegistrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an event registration."""
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]


class AttendanceListCreateView(generics.ListCreateAPIView):
    """List and create attendance records."""
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'student', 'attendance_status']
    search_fields = ['student__first_name', 'student__last_name', 'event__title']
    ordering_fields = ['check_in_time']
    ordering = ['-check_in_time']
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return AttendanceCreateSerializer
        return AttendanceSerializer


class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an attendance record."""
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]


class FeedbackListCreateView(generics.ListCreateAPIView):
    """List and create feedback records."""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'student', 'rating']
    search_fields = ['student__first_name', 'student__last_name', 'event__title', 'comments']
    ordering_fields = ['submitted_at', 'rating']
    ordering = ['-submitted_at']
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return FeedbackCreateSerializer
        return FeedbackSerializer


class FeedbackDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a feedback record."""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]


# Custom API endpoints

@api_view(['POST'])
@permission_classes([AllowAny])
def register_for_event(request, event_id):
    """Register a student for an event."""
    try:
        event = Event.objects.get(id=event_id)
        student_id = request.data.get('student_id')
        
        if not student_id:
            return Response({'error': 'Student ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already registered
        if EventRegistration.objects.filter(event=event, student=student).exists():
            return Response({'error': 'Student is already registered for this event'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check if registration is open
        if not event.is_registration_open:
            return Response({'error': 'Registration is not open for this event'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check if event is full
        if event.is_full:
            return Response({'error': 'Event is at full capacity'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        registration = EventRegistration.objects.create(event=event, student=student)
        serializer = EventRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_in_student(request, event_id):
    """Check in a student for an event."""
    try:
        event = Event.objects.get(id=event_id)
        student_id = request.data.get('student_id')
        
        if not student_id:
            return Response({'error': 'Student ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if student is registered
        if not EventRegistration.objects.filter(event=event, student=student, status='registered').exists():
            return Response({'error': 'Student is not registered for this event'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already checked in
        if Attendance.objects.filter(event=event, student=student).exists():
            return Response({'error': 'Student is already checked in'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        attendance = Attendance.objects.create(
            event=event, 
            student=student, 
            marked_by=request.user,
            attendance_status='present'
        )
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_feedback(request, event_id):
    """Submit feedback for an event."""
    try:
        event = Event.objects.get(id=event_id)
        student_id = request.data.get('student_id')
        rating = request.data.get('rating')
        comments = request.data.get('comments', '')
        
        if not student_id:
            return Response({'error': 'Student ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not rating:
            return Response({'error': 'Rating is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if student attended the event
        if not Attendance.objects.filter(event=event, student=student, attendance_status='present').exists():
            return Response({'error': 'Student must have attended the event to provide feedback'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check if feedback already exists
        if Feedback.objects.filter(event=event, student=student).exists():
            return Response({'error': 'Feedback already submitted for this event'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        feedback = Feedback.objects.create(
            event=event, 
            student=student, 
            rating=rating, 
            comments=comments
        )
        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_registrations(request, event_id):
    """Get all registrations for a specific event."""
    try:
        event = Event.objects.get(id=event_id)
        registrations = EventRegistration.objects.filter(event=event)
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_attendance(request, event_id):
    """Get all attendance records for a specific event."""
    try:
        event = Event.objects.get(id=event_id)
        attendance = Attendance.objects.filter(event=event)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_feedback(request, event_id):
    """Get all feedback for a specific event."""
    try:
        event = Event.objects.get(id=event_id)
        feedback = Feedback.objects.filter(event=event)
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_events(request, student_id):
    """Get all events for a specific student."""
    try:
        student = Student.objects.get(id=student_id)
        registrations = EventRegistration.objects.filter(student=student)
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def event_popularity_report(request):
    """Generate event popularity report."""
    
    # Get query parameters
    college_id = request.GET.get('college_id')
    event_type = request.GET.get('event_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    limit = int(request.GET.get('limit', 10))
    
    # Build base queryset
    events = Event.objects.all()
    
    if college_id:
        events = events.filter(college_id=college_id)
    if event_type:
        events = events.filter(event_type=event_type)
    if start_date:
        events = events.filter(start_date__date__gte=start_date)
    if end_date:
        events = events.filter(start_date__date__lte=end_date)
    
    # Get event popularity data
    popularity_data = events.annotate(
        total_registrations=Count('registrations', filter=Q(registrations__status='registered')),
        total_attendance=Count('attendance', filter=Q(attendance__attendance_status='present')),
        avg_rating=Avg('feedback__rating')
    ).order_by('-total_registrations')[:limit]
    
    # Format response
    report_data = []
    for event in popularity_data:
        attendance_rate = 0
        if event.total_registrations > 0:
            attendance_rate = (event.total_attendance / event.total_registrations) * 100
        
        report_data.append({
            'event_id': event.id,
            'event_code': event.event_code,
            'title': event.title,
            'college_name': event.college.name,
            'college_code': event.college.code,
            'event_type': event.event_type,
            'start_date': event.start_date.isoformat(),
            'location': event.location,
            'total_registrations': event.total_registrations,
            'total_attendance': event.total_attendance,
            'attendance_rate': round(attendance_rate, 2),
            'avg_rating': round(event.avg_rating or 0, 2)
        })
    
    return Response({
        'report_type': 'event_popularity',
        'data': report_data,
        'total_events': len(report_data)
    })
