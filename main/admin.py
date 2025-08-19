from django.contrib import admin
from .models import StudentProfile, Subject, StudentSubject, Result, Attendance

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'user', 'course', 'semester', 'profile_completed']
    list_filter = ['profile_completed', 'course', 'semester']
    search_fields = ['roll_number', 'user__username', 'user__first_name', 'user__last_name']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits']
    search_fields = ['code', 'name']

@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'enrolled_date']
    list_filter = ['subject', 'enrolled_date']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'marks_obtained', 'grade', 'exam_date']
    list_filter = ['grade', 'exam_date', 'subject']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'attendance_percentage', 'month', 'year']
    list_filter = ['month', 'year', 'subject']