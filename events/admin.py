"""
Admin configuration for events app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import College, Student, Event, EventRegistration, Attendance, Feedback, AdminUser


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_email', 'contact_phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['code', 'name', 'contact_email']
    ordering = ['code']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'college', 'department', 'year_of_study', 'email']
    list_filter = ['college', 'department', 'year_of_study', 'created_at']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
    ordering = ['college', 'last_name', 'first_name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_code', 'title', 'college', 'event_type', 'start_date', 'status', 'registration_count']
    list_filter = ['college', 'event_type', 'status', 'start_date']
    search_fields = ['event_code', 'title', 'description']
    ordering = ['-start_date']
    readonly_fields = ['event_code', 'created_at', 'updated_at']
    
    def registration_count(self, obj):
        return obj.current_registrations_count
    registration_count.short_description = 'Registrations'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['student', 'event', 'status', 'registration_date']
    list_filter = ['status', 'registration_date', 'event__college', 'event__event_type']
    search_fields = ['student__first_name', 'student__last_name', 'event__title']
    ordering = ['-registration_date']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'event', 'attendance_status', 'check_in_time', 'check_out_time']
    list_filter = ['attendance_status', 'check_in_time', 'event__college', 'event__event_type']
    search_fields = ['student__first_name', 'student__last_name', 'event__title']
    ordering = ['-check_in_time']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['student', 'event', 'rating', 'submitted_at']
    list_filter = ['rating', 'submitted_at', 'event__college', 'event__event_type']
    search_fields = ['student__first_name', 'student__last_name', 'event__title', 'comments']
    ordering = ['-submitted_at']


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'college', 'role', 'is_active', 'created_at']
    list_filter = ['college', 'role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['college', 'user__username']

