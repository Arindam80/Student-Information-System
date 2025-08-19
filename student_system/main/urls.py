from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Student URLs
    path('student/register/', views.student_register, name='student_register'),
    path('student/login/', views.student_login_view, name='student_login'),
    path('student/logout/', views.custom_logout_view, name='student_logout'),
    path('student/ajax-logout/', views.ajax_logout_view, name='ajax_logout'),  # Alternative AJAX logout
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Admin URLs
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/students/', views.student_list, name='student_list'),
    path('admin-panel/student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('admin-panel/student/<int:student_id>/add-subject/', views.add_subject_to_student, name='add_subject_to_student'),
    path('admin-panel/student/<int:student_id>/add-result/', views.add_result, name='add_result'),
    path('admin-panel/student/<int:student_id>/add-attendance/', views.add_attendance, name='add_attendance'),
    path('admin-panel/student/<int:student_id>/delete/', views.delete_student, name='delete_student'),
]