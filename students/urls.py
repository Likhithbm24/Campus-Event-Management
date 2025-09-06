"""
URL configuration for students app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('students/<int:student_id>/profile/', views.student_profile, name='student-profile'),
    path('students/<int:student_id>/events/', views.student_events, name='student-events'),
    path('students/<int:student_id>/attendance/', views.student_attendance, name='student-attendance'),
    path('students/<int:student_id>/feedback/', views.student_feedback, name='student-feedback'),
]

