"""
Main views for the Campus Event Management Platform.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from events.models import Event, College, Student, EventRegistration, Attendance, Feedback
from django.db.models import Avg, Count
import json


def home(request):
    """Home page view."""
    return render(request, 'home.html')


@login_required
def admin_dashboard(request):
    """Admin dashboard view."""
    return render(request, 'admin/dashboard.html')


def student_login(request):
    """Student login page."""
    return render(request, 'student/login.html')


def student_dashboard(request):
    """Student dashboard view."""
    return render(request, 'student/dashboard.html')


def student_credentials_debug(request):
    """Debug endpoint to show available student credentials."""
    students = Student.objects.all()[:10].values('student_id', 'email', 'first_name', 'last_name', 'college__name')
    return JsonResponse({
        'message': 'Available student credentials for testing:',
        'students': list(students)
    })


@login_required
def get_colleges_for_admin(request):
    """Get colleges for admin dashboard dropdown."""
    colleges = College.objects.all().values('id', 'code', 'name')
    return JsonResponse({'colleges': list(colleges)})


@require_http_methods(["POST"])
def process_student_login(request):
    """Process student login."""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        email = data.get('email')
        
        if not student_id or not email:
            return JsonResponse({'error': 'Student ID and email are required'}, status=400)
        
        try:
            student = Student.objects.get(student_id=student_id, email=email)
        except Student.DoesNotExist:
            # Check if student ID exists but email is wrong
            if Student.objects.filter(student_id=student_id).exists():
                return JsonResponse({'error': 'Invalid email for this student ID'}, status=401)
            # Check if email exists but student ID is wrong
            elif Student.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Invalid student ID for this email'}, status=401)
            else:
                return JsonResponse({'error': 'Student not found. Please check your credentials.'}, status=401)
        
        return JsonResponse({
            'success': True,
            'student_id': student.student_id,
            'student_name': student.full_name,
            'student_email': student.email,
            'student_college': student.college.name,
            'student_db_id': student.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_event_from_admin(request):
    """Create event from admin dashboard."""
    try:
        data = json.loads(request.body)
        
        # Get the college
        college_id = data.get('college')
        if not college_id:
            return JsonResponse({'error': 'College is required'}, status=400)
        
        try:
            college = College.objects.get(id=college_id)
        except College.DoesNotExist:
            return JsonResponse({'error': 'Invalid college'}, status=400)
        
        # Parse dates
        start_date = parse_datetime(data.get('start_date'))
        end_date = parse_datetime(data.get('end_date'))
        registration_start_date = parse_datetime(data.get('registration_start_date')) if data.get('registration_start_date') else None
        registration_deadline = parse_datetime(data.get('registration_deadline')) if data.get('registration_deadline') else None
        
        if not start_date or not end_date:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
        
        # Create the event
        event = Event.objects.create(
            college=college,
            title=data.get('title'),
            description=data.get('description', ''),
            event_type=data.get('event_type'),
            start_date=start_date,
            end_date=end_date,
            location=data.get('location', ''),
            max_participants=int(data.get('max_capacity', 100)),
            registration_start_date=registration_start_date,
            registration_deadline=registration_deadline,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Event created successfully',
            'event_id': event.id,
            'event_code': event.event_code
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error creating event: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def end_event(request, event_id):
    """End an event (mark as completed)."""
    try:
        event = Event.objects.get(id=event_id)
        event.status = 'completed'
        event.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Event ended successfully',
            'event_id': event.id,
            'status': event.status
        })
        
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error ending event: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def cancel_event(request, event_id):
    """Cancel an event."""
    try:
        event = Event.objects.get(id=event_id)
        event.status = 'cancelled'
        event.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Event cancelled successfully',
            'event_id': event.id,
            'status': event.status
        })
        
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error cancelling event: {str(e)}'}, status=500)


@login_required
def event_attendance(request, event_id):
    """Mark attendance for an event."""
    try:
        event = Event.objects.get(id=event_id)
        # Get all students registered for this event
        registrations = EventRegistration.objects.filter(event=event, status='registered')
        students = [reg.student for reg in registrations]
        
        # Get existing attendance records
        attendance_records = Attendance.objects.filter(event=event)
        attendance_dict = {record.student.id: record for record in attendance_records}
        
        context = {
            'event': event,
            'students': students,
            'attendance_records': attendance_dict,
        }
        
        return render(request, 'admin/attendance.html', context)
        
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def mark_student_attendance(request, event_id):
    """Mark attendance for a specific student."""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        status = data.get('status', 'present')
        notes = data.get('notes', '')
        
        event = Event.objects.get(id=event_id)
        student = Student.objects.get(id=student_id)
        
        # Create or update attendance record
        attendance, created = Attendance.objects.get_or_create(
            event=event,
            student=student,
            defaults={
                'attendance_status': status,
                'marked_by': request.user,
                'notes': notes
            }
        )
        
        if not created:
            attendance.attendance_status = status
            attendance.marked_by = request.user
            attendance.notes = notes
            attendance.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Attendance marked as {status}',
            'student_name': student.full_name,
            'status': status
        })
        
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error marking attendance: {str(e)}'}, status=500)


@login_required
def edit_event(request, event_id):
    """Edit event page."""
    try:
        event = Event.objects.get(id=event_id)
        colleges = College.objects.all().order_by('name')
        
        context = {
            'event': event,
            'colleges': colleges,
        }
        
        return render(request, 'admin/edit_event.html', context)
        
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def update_event(request, event_id):
    """Update event data."""
    try:
        data = json.loads(request.body)
        
        event = Event.objects.get(id=event_id)
        
        # Update event fields
        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)
        event.location = data.get('location', event.location)
        event.max_participants = int(data.get('max_capacity', event.max_participants))
        
        # Update dates
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        registration_start_date_str = data.get('registration_start_date')
        registration_deadline_str = data.get('registration_deadline')
        
        if start_date_str:
            event.start_date = parse_datetime(start_date_str)
        if end_date_str:
            event.end_date = parse_datetime(end_date_str)
        if registration_start_date_str:
            event.registration_start_date = parse_datetime(registration_start_date_str)
        if registration_deadline_str:
            event.registration_deadline = parse_datetime(registration_deadline_str)
        
        # Update college
        college_id = data.get('college_id')
        if college_id:
            college = College.objects.get(id=college_id)
            event.college = college
        
        # Update status
        status = data.get('status')
        if status in ['active', 'completed', 'cancelled']:
            event.status = status
        
        event.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Event updated successfully',
            'event_id': event.id
        })
        
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except College.DoesNotExist:
        return JsonResponse({'error': 'College not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error updating event: {str(e)}'}, status=500)


@login_required
def feedback_analytics(request):
    """View for feedback analytics dashboard."""
    return render(request, 'admin/feedback_analytics.html')


@login_required
def get_feedback_analytics(request):
    """API endpoint to get feedback analytics data."""
    try:
        # Get all events with feedback
        events_with_feedback = Event.objects.filter(feedback__isnull=False).distinct()
        
        # Calculate overall statistics
        total_feedback = Feedback.objects.count()
        avg_rating = Feedback.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Get rating distribution
        rating_distribution = Feedback.objects.values('rating').annotate(
            count=Count('id')
        ).order_by('rating')
        
        # Get feedback by event type
        feedback_by_type = events_with_feedback.values('event_type').annotate(
            total_feedback=Count('feedback'),
            avg_rating=Avg('feedback__rating')
        ).order_by('-total_feedback')
        
        # Get feedback by college
        feedback_by_college = events_with_feedback.values('college__name', 'college__code').annotate(
            total_feedback=Count('feedback'),
            avg_rating=Avg('feedback__rating')
        ).order_by('-total_feedback')
        
        # Get top rated events
        top_rated_events = events_with_feedback.annotate(
            avg_rating=Avg('feedback__rating'),
            feedback_count=Count('feedback')
        ).filter(feedback_count__gte=3).order_by('-avg_rating')[:10]
        
        # Get recent feedback
        recent_feedback = Feedback.objects.select_related('event', 'student').order_by('-submitted_at')[:10]
        
        # Format top rated events
        top_events_data = []
        for event in top_rated_events:
            top_events_data.append({
                'id': event.id,
                'title': event.title,
                'event_code': event.event_code,
                'college': event.college.name,
                'event_type': event.event_type,
                'avg_rating': round(event.avg_rating, 2),
                'feedback_count': event.feedback_count
            })
        
        # Format recent feedback
        recent_feedback_data = []
        for feedback in recent_feedback:
            recent_feedback_data.append({
                'id': feedback.id,
                'event_title': feedback.event.title,
                'student_name': feedback.student.full_name,
                'rating': feedback.rating,
                'comments': feedback.comments[:100] + '...' if len(feedback.comments) > 100 else feedback.comments,
                'submitted_at': feedback.submitted_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'total_feedback': total_feedback,
                'avg_rating': round(avg_rating, 2),
                'rating_distribution': list(rating_distribution),
                'feedback_by_type': list(feedback_by_type),
                'feedback_by_college': list(feedback_by_college),
                'top_rated_events': top_events_data,
                'recent_feedback': recent_feedback_data
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error getting feedback analytics: {str(e)}'}, status=500)


@login_required
def event_feedback_details(request, event_id):
    """View for detailed feedback of a specific event."""
    try:
        event = Event.objects.get(id=event_id)
        feedback_records = Feedback.objects.filter(event=event).select_related('student').order_by('-submitted_at')
        
        # Calculate event-specific statistics
        total_feedback = feedback_records.count()
        avg_rating = feedback_records.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Get rating distribution for this event
        rating_distribution = feedback_records.values('rating').annotate(
            count=Count('id')
        ).order_by('rating')
        
        # Format feedback records
        feedback_data = []
        for feedback in feedback_records:
            feedback_data.append({
                'id': feedback.id,
                'student_name': feedback.student.full_name,
                'student_id': feedback.student.student_id,
                'college': feedback.student.college.name,
                'rating': feedback.rating,
                'comments': feedback.comments,
                'submitted_at': feedback.submitted_at.strftime('%Y-%m-%d %H:%M')
            })
        
        context = {
            'event': event,
            'feedback_records': feedback_data,
            'total_feedback': total_feedback,
            'avg_rating': round(avg_rating, 2),
            'rating_distribution': list(rating_distribution)
        }
        
        return render(request, 'admin/event_feedback_details.html', context)
        
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error getting event feedback: {str(e)}'}, status=500)
