"""
Reporting views for analytics and insights.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta

from events.models import College, Student, Event, EventRegistration, Attendance, Feedback


@api_view(['GET'])
@permission_classes([AllowAny])
def event_popularity_report(request):
    """Generate event popularity report."""
    
    # Get query parameters
    college_id = request.GET.get('college_id')
    event_type = request.GET.get('event_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
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
    ).order_by('-total_registrations')
    
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
            'college': event.college.name,
            'event_type': event.event_type,
            'start_date': event.start_date,
            'total_registrations': event.total_registrations,
            'total_attendance': event.total_attendance,
            'attendance_rate': round(attendance_rate, 2),
            'avg_rating': round(event.avg_rating or 0, 2),
            'max_participants': event.max_participants,
            'is_full': event.is_full
        })
    
    return Response({
        'report_type': 'event_popularity',
        'total_events': len(report_data),
        'filters_applied': {
            'college_id': college_id,
            'event_type': event_type,
            'start_date': start_date,
            'end_date': end_date
        },
        'data': report_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_participation_report(request):
    """Generate student participation report."""
    
    # Get query parameters
    college_id = request.GET.get('college_id')
    department = request.GET.get('department')
    year_of_study = request.GET.get('year_of_study')
    min_events = int(request.GET.get('min_events', 1))
    
    # Build base queryset
    students = Student.objects.all()
    
    if college_id:
        students = students.filter(college_id=college_id)
    if department:
        students = students.filter(department=department)
    if year_of_study:
        students = students.filter(year_of_study=year_of_study)
    
    # Get student participation data
    participation_data = students.annotate(
        total_registrations=Count('registrations', filter=Q(registrations__status='registered')),
        total_attendance=Count('attendance', filter=Q(attendance__attendance_status='present')),
        avg_rating_given=Avg('feedback__rating')
    ).filter(total_registrations__gte=min_events).order_by('-total_registrations')
    
    # Format response
    report_data = []
    for student in participation_data:
        attendance_rate = 0
        if student.total_registrations > 0:
            attendance_rate = (student.total_attendance / student.total_registrations) * 100
        
        report_data.append({
            'student_id': student.id,
            'student_code': student.student_id,
            'full_name': student.full_name,
            'college': student.college.name,
            'department': student.department,
            'year_of_study': student.year_of_study,
            'total_registrations': student.total_registrations,
            'total_attendance': student.total_attendance,
            'attendance_rate': round(attendance_rate, 2),
            'avg_rating_given': round(student.avg_rating_given or 0, 2)
        })
    
    return Response({
        'report_type': 'student_participation',
        'total_students': len(report_data),
        'filters_applied': {
            'college_id': college_id,
            'department': department,
            'year_of_study': year_of_study,
            'min_events': min_events
        },
        'data': report_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_summary_report(request):
    """Generate attendance summary report."""
    
    # Get query parameters
    college_id = request.GET.get('college_id')
    event_type = request.GET.get('event_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
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
    
    # Calculate overall statistics
    total_events = events.count()
    total_registrations = EventRegistration.objects.filter(
        event__in=events, status='registered'
    ).count()
    total_attendance = Attendance.objects.filter(
        event__in=events, attendance_status='present'
    ).count()
    
    overall_attendance_rate = 0
    if total_registrations > 0:
        overall_attendance_rate = (total_attendance / total_registrations) * 100
    
    # Get attendance by event type
    attendance_by_type = events.values('event_type').annotate(
        event_count=Count('id'),
        total_registrations=Count('registrations', filter=Q(registrations__status='registered')),
        total_attendance=Count('attendance', filter=Q(attendance__attendance_status='present'))
    ).order_by('event_type')
    
    # Calculate attendance rate for each event type
    type_data = []
    for item in attendance_by_type:
        attendance_rate = 0
        if item['total_registrations'] > 0:
            attendance_rate = (item['total_attendance'] / item['total_registrations']) * 100
        
        type_data.append({
            'event_type': item['event_type'],
            'event_count': item['event_count'],
            'total_registrations': item['total_registrations'],
            'total_attendance': item['total_attendance'],
            'attendance_rate': round(attendance_rate, 2)
        })
    
    # Get attendance by college
    attendance_by_college = events.values('college__name', 'college__code').annotate(
        event_count=Count('id'),
        total_registrations=Count('registrations', filter=Q(registrations__status='registered')),
        total_attendance=Count('attendance', filter=Q(attendance__attendance_status='present'))
    ).order_by('college__name')
    
    # Calculate attendance rate for each college
    college_data = []
    for item in attendance_by_college:
        attendance_rate = 0
        if item['total_registrations'] > 0:
            attendance_rate = (item['total_attendance'] / item['total_registrations']) * 100
        
        college_data.append({
            'college_code': item['college__code'],
            'college_name': item['college__name'],
            'event_count': item['event_count'],
            'total_registrations': item['total_registrations'],
            'total_attendance': item['total_attendance'],
            'attendance_rate': round(attendance_rate, 2)
        })
    
    return Response({
        'report_type': 'attendance_summary',
        'overall_statistics': {
            'total_events': total_events,
            'total_registrations': total_registrations,
            'total_attendance': total_attendance,
            'overall_attendance_rate': round(overall_attendance_rate, 2)
        },
        'attendance_by_event_type': type_data,
        'attendance_by_college': college_data,
        'filters_applied': {
            'college_id': college_id,
            'event_type': event_type,
            'start_date': start_date,
            'end_date': end_date
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_scores_report(request):
    """Generate feedback scores report."""
    
    # Get query parameters
    college_id = request.GET.get('college_id')
    event_type = request.GET.get('event_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_rating = int(request.GET.get('min_rating', 1))
    max_rating = int(request.GET.get('max_rating', 5))
    
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
    
    # Get feedback data
    feedback_data = Feedback.objects.filter(
        event__in=events,
        rating__gte=min_rating,
        rating__lte=max_rating
    )
    
    # Calculate overall statistics
    total_feedback = feedback_data.count()
    avg_rating = feedback_data.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Get rating distribution
    rating_distribution = feedback_data.values('rating').annotate(
        count=Count('id')
    ).order_by('rating')
    
    # Get feedback by event type
    feedback_by_type = events.values('event_type').annotate(
        total_feedback=Count('feedback'),
        avg_rating=Avg('feedback__rating')
    ).filter(total_feedback__gt=0).order_by('event_type')
    
    # Get feedback by college
    feedback_by_college = events.values('college__name', 'college__code').annotate(
        total_feedback=Count('feedback'),
        avg_rating=Avg('feedback__rating')
    ).filter(total_feedback__gt=0).order_by('college__name')
    
    # Get top and bottom rated events
    top_rated_events = events.annotate(
        avg_rating=Avg('feedback__rating'),
        feedback_count=Count('feedback')
    ).filter(feedback_count__gt=0).order_by('-avg_rating')[:10]
    
    bottom_rated_events = events.annotate(
        avg_rating=Avg('feedback__rating'),
        feedback_count=Count('feedback')
    ).filter(feedback_count__gt=0).order_by('avg_rating')[:10]
    
    return Response({
        'report_type': 'feedback_scores',
        'overall_statistics': {
            'total_feedback': total_feedback,
            'avg_rating': round(avg_rating, 2),
            'rating_range': f"{min_rating}-{max_rating}"
        },
        'rating_distribution': list(rating_distribution),
        'feedback_by_event_type': [
            {
                'event_type': item['event_type'],
                'total_feedback': item['total_feedback'],
                'avg_rating': round(item['avg_rating'] or 0, 2)
            }
            for item in feedback_by_type
        ],
        'feedback_by_college': [
            {
                'college_code': item['college__code'],
                'college_name': item['college__name'],
                'total_feedback': item['total_feedback'],
                'avg_rating': round(item['avg_rating'] or 0, 2)
            }
            for item in feedback_by_college
        ],
        'top_rated_events': [
            {
                'event_id': event.id,
                'event_code': event.event_code,
                'title': event.title,
                'college': event.college.name,
                'avg_rating': round(event.avg_rating or 0, 2),
                'feedback_count': event.feedback_count
            }
            for event in top_rated_events
        ],
        'bottom_rated_events': [
            {
                'event_id': event.id,
                'event_code': event.event_code,
                'title': event.title,
                'college': event.college.name,
                'avg_rating': round(event.avg_rating or 0, 2),
                'feedback_count': event.feedback_count
            }
            for event in bottom_rated_events
        ],
        'filters_applied': {
            'college_id': college_id,
            'event_type': event_type,
            'start_date': start_date,
            'end_date': end_date,
            'min_rating': min_rating,
            'max_rating': max_rating
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def college_summary_report(request, college_id):
    """Generate comprehensive summary report for a specific college."""
    
    try:
        college = College.objects.get(id=college_id)
    except College.DoesNotExist:
        return Response({'error': 'College not found'}, status=404)
    
    # Get college events
    events = Event.objects.filter(college=college)
    
    # Calculate basic statistics
    total_events = events.count()
    active_events = events.filter(status='active').count()
    completed_events = events.filter(status='completed').count()
    cancelled_events = events.filter(status='cancelled').count()
    
    # Calculate registration statistics
    total_registrations = EventRegistration.objects.filter(
        event__in=events, status='registered'
    ).count()
    
    # Calculate attendance statistics
    total_attendance = Attendance.objects.filter(
        event__in=events, attendance_status='present'
    ).count()
    
    attendance_rate = 0
    if total_registrations > 0:
        attendance_rate = (total_attendance / total_registrations) * 100
    
    # Calculate feedback statistics
    total_feedback = Feedback.objects.filter(event__in=events).count()
    avg_rating = Feedback.objects.filter(event__in=events).aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0
    
    # Get event type breakdown
    event_type_breakdown = events.values('event_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get monthly event trends (last 12 months)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_trends = events.filter(
        start_date__gte=twelve_months_ago
    ).extra(
        select={'month': "EXTRACT(month FROM start_date)", 'year': "EXTRACT(year FROM start_date)"}
    ).values('year', 'month').annotate(
        event_count=Count('id')
    ).order_by('year', 'month')
    
    # Get top performing events
    top_events = events.annotate(
        registration_count=Count('registrations', filter=Q(registrations__status='registered')),
        attendance_count=Count('attendance', filter=Q(attendance__attendance_status='present')),
        avg_rating=Avg('feedback__rating')
    ).order_by('-registration_count')[:5]
    
    # Get student participation by department
    student_participation = Student.objects.filter(college=college).values('department').annotate(
        total_students=Count('id'),
        active_participants=Count('registrations', filter=Q(registrations__status='registered'))
    ).order_by('-active_participants')
    
    return Response({
        'report_type': 'college_summary',
        'college': {
            'id': college.id,
            'code': college.code,
            'name': college.name
        },
        'overview': {
            'total_events': total_events,
            'active_events': active_events,
            'completed_events': completed_events,
            'cancelled_events': cancelled_events,
            'total_registrations': total_registrations,
            'total_attendance': total_attendance,
            'attendance_rate': round(attendance_rate, 2),
            'total_feedback': total_feedback,
            'avg_rating': round(avg_rating, 2)
        },
        'event_type_breakdown': list(event_type_breakdown),
        'monthly_trends': list(monthly_trends),
        'top_events': [
            {
                'event_id': event.id,
                'event_code': event.event_code,
                'title': event.title,
                'event_type': event.event_type,
                'registration_count': event.registration_count,
                'attendance_count': event.attendance_count,
                'avg_rating': round(event.avg_rating or 0, 2)
            }
            for event in top_events
        ],
        'student_participation_by_department': [
            {
                'department': item['department'] or 'Unknown',
                'total_students': item['total_students'],
                'active_participants': item['active_participants']
            }
            for item in student_participation
        ]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_summary(request):
    """Generate dashboard summary with key metrics."""
    
    # Overall statistics
    total_colleges = College.objects.count()
    total_students = Student.objects.count()
    total_events = Event.objects.count()
    active_events = Event.objects.filter(status='active').count()
    total_registrations = EventRegistration.objects.filter(status='registered').count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_registrations = EventRegistration.objects.filter(
        registration_date__gte=thirty_days_ago
    ).count()
    recent_attendance = Attendance.objects.filter(
        check_in_time__gte=thirty_days_ago
    ).count()
    recent_feedback = Feedback.objects.filter(
        submitted_at__gte=thirty_days_ago
    ).count()
    
    # Top performing colleges
    top_colleges = College.objects.annotate(
        event_count=Count('events'),
        registration_count=Count('events__registrations', filter=Q(events__registrations__status='registered')),
        avg_rating=Avg('events__feedback__rating')
    ).filter(event_count__gt=0).order_by('-registration_count')[:5]
    
    # Event type popularity
    event_type_popularity = Event.objects.values('event_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get recent registrations for display
    recent_registration_details = EventRegistration.objects.filter(
        registration_date__gte=thirty_days_ago
    ).select_related('student', 'event', 'event__college').order_by('-registration_date')[:10]
    
    recent_registrations_list = [
        {
            'id': reg.id,
            'student_name': reg.student.full_name,
            'student_id': reg.student.student_id,
            'event_title': reg.event.title,
            'event_code': reg.event.event_code,
            'college_name': reg.event.college.name,
            'registration_date': reg.registration_date.strftime('%Y-%m-%d %H:%M'),
            'status': reg.status
        }
        for reg in recent_registration_details
    ]
    
    return Response({
        'report_type': 'dashboard_summary',
        'overview': {
            'total_colleges': total_colleges,
            'total_students': total_students,
            'total_events': total_events,
            'active_events': active_events,
            'total_registrations': total_registrations
        },
        'recent_activity': {
            'period': 'Last 30 days',
            'registrations': recent_registrations,
            'attendance': recent_attendance,
            'feedback': recent_feedback
        },
        'top_colleges': [
            {
                'college_id': college.id,
                'college_code': college.code,
                'college_name': college.name,
                'event_count': college.event_count,
                'registration_count': college.registration_count,
                'avg_rating': round(college.avg_rating or 0, 2)
            }
            for college in top_colleges
        ],
        'recent_registrations': recent_registrations_list,
        'event_type_popularity': list(event_type_popularity)
    })

