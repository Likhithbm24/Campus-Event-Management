"""
URL configuration for campus_events project.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/colleges/', views.get_colleges_for_admin, name='get-colleges-for-admin'),
    path('admin/create-event/', views.create_event_from_admin, name='create-event-from-admin'),
    path('admin/events/<int:event_id>/end/', views.end_event, name='end-event'),
    path('admin/events/<int:event_id>/cancel/', views.cancel_event, name='cancel-event'),
    path('admin/events/<int:event_id>/attendance/', views.event_attendance, name='event-attendance'),
    path('admin/events/<int:event_id>/attendance/mark/', views.mark_student_attendance, name='mark-student-attendance'),
    path('admin/events/<int:event_id>/edit/', views.edit_event, name='edit-event'),
    path('admin/events/<int:event_id>/update/', views.update_event, name='update-event'),
    path('admin/feedback-analytics/', views.feedback_analytics, name='feedback-analytics'),
    path('admin/api/feedback-analytics/', views.get_feedback_analytics, name='get-feedback-analytics'),
    path('admin/events/<int:event_id>/feedback/', views.event_feedback_details, name='event-feedback-details'),
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('student/login/', views.student_login, name='student-login'),
    path('student/login/process/', views.process_student_login, name='process-student-login'),
    path('student/dashboard/', views.student_dashboard, name='student-dashboard'),
    path('student/credentials/', views.student_credentials_debug, name='student-credentials-debug'),
    # path('api/auth/', include('rest_framework_simplejwt.urls')),
    path('api/', include('events.urls')),
    path('api/', include('students.urls')),
    path('api/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
