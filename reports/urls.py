"""
URL configuration for reports app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('events/popularity/', views.event_popularity_report, name='event-popularity-report'),
    path('students/participation/', views.student_participation_report, name='student-participation-report'),
    path('attendance/summary/', views.attendance_summary_report, name='attendance-summary-report'),
    path('feedback/scores/', views.feedback_scores_report, name='feedback-scores-report'),
    path('college/<int:college_id>/summary/', views.college_summary_report, name='college-summary-report'),
    path('dashboard/summary/', views.dashboard_summary, name='dashboard-summary'),
]

