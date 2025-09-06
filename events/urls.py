"""
URL configuration for events app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    # College endpoints
    path('colleges/', views.CollegeListCreateView.as_view(), name='college-list-create'),
    path('colleges/<int:pk>/', views.CollegeDetailView.as_view(), name='college-detail'),
    
    # Student endpoints
    path('students/', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('students/<int:student_id>/events/', views.student_events, name='student-events'),
    
    # Event endpoints
    path('events/', views.EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/<int:event_id>/registrations/', views.event_registrations, name='event-registrations'),
    path('events/<int:event_id>/attendance/', views.event_attendance, name='event-attendance'),
    path('events/<int:event_id>/feedback/', views.event_feedback, name='event-feedback'),
    
    # Event registration endpoints
    path('registrations/', views.EventRegistrationListCreateView.as_view(), name='registration-list-create'),
    path('registrations/<int:pk>/', views.EventRegistrationDetailView.as_view(), name='registration-detail'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register-for-event'),
    
    # Attendance endpoints
    path('attendance/', views.AttendanceListCreateView.as_view(), name='attendance-list-create'),
    path('attendance/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance-detail'),
    path('events/<int:event_id>/checkin/', views.check_in_student, name='check-in-student'),
    
    # Feedback endpoints
    path('feedback/', views.FeedbackListCreateView.as_view(), name='feedback-list-create'),
    path('feedback/<int:pk>/', views.FeedbackDetailView.as_view(), name='feedback-detail'),
    path('events/<int:event_id>/feedback/submit/', views.submit_feedback, name='submit-feedback'),
    
    # Report endpoints
    path('events/popularity/', views.event_popularity_report, name='event-popularity-report'),
]

