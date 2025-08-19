from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import StudentProfile, Subject, StudentSubject, Result, Attendance
from .forms import StudentRegistrationForm, StudentProfileForm, ResultForm, AttendanceForm

@never_cache
def home(request):
    return render(request, 'home.html')

@never_cache
@csrf_protect
def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Registration successful! Please wait for admin approval.')
                return redirect('student_login')
            except IntegrityError:
                messages.error(request, 'Roll number already exists!')
    else:
        form = StudentRegistrationForm()
    return render(request, 'student/register.html', {'form': form})

@never_cache
@csrf_protect
def student_login_view(request):
    # If user is already authenticated, redirect them
    if request.user.is_authenticated:
        if hasattr(request.user, 'studentprofile'):
            return redirect('student_dashboard')
        elif request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'studentprofile'):
                login(request, user)
                return redirect('student_dashboard')
            elif user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access denied.')
        else:
            messages.error(request, 'Invalid credentials.')
    
    return render(request, 'student/login.html')

@require_POST
@csrf_protect
def custom_logout_view(request):
    """Custom logout view with proper session clearing and cache control"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    
    # Return a redirect response directly
    response = redirect('home')
    
    # Add cache-busting headers
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['Last-Modified'] = '0'
    response['X-Frame-Options'] = 'DENY'
    
    return response

# Alternative AJAX logout view for better UX
@require_POST
@csrf_protect
def ajax_logout_view(request):
    """AJAX logout view that returns JSON response"""
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({
            'success': True, 
            'message': 'Successfully logged out',
            'redirect_url': reverse('student_login')
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'User not authenticated'
        })

@never_cache
@login_required
def student_dashboard(request):
    # Double-check authentication
    if not request.user.is_authenticated:
        return redirect('student_login')
        
    if not hasattr(request.user, 'studentprofile'):
        messages.error(request, 'Access denied.')
        logout(request)
        return redirect('student_login')
    
    student_profile = request.user.studentprofile
    subjects = StudentSubject.objects.filter(student=student_profile).select_related('subject')
    results = Result.objects.filter(student=student_profile).select_related('subject')
    attendance_records = Attendance.objects.filter(student=student_profile).select_related('subject')
    
    context = {
        'student': student_profile,
        'subjects': subjects,
        'results': results,
        'attendance_records': attendance_records,
    }
    return render(request, 'student/dashboard.html', context)

def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser

@never_cache
@user_passes_test(is_staff_or_superuser)
def admin_dashboard(request):
    # Double-check authentication and permissions
    if not request.user.is_authenticated:
        return redirect('student_login')
    
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        logout(request)
        return redirect('student_login')
    
    total_students = StudentProfile.objects.count()
    pending_students = StudentProfile.objects.filter(profile_completed=False).count()
    completed_students = StudentProfile.objects.filter(profile_completed=True).count()
    total_subjects = Subject.objects.count()
    
    context = {
        'total_students': total_students,
        'pending_students': pending_students,
        'completed_students': completed_students,
        'total_subjects': total_subjects,
    }
    return render(request, 'admin_panel/admin_dashboard.html', context)

@never_cache
@user_passes_test(is_staff_or_superuser)
def student_list(request):
    students = StudentProfile.objects.select_related('user').all()
    return render(request, 'admin_panel/student_list.html', {'students': students})

@user_passes_test(is_staff_or_superuser)
def student_detail(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    
    if request.method == 'POST':
        profile_form = StudentProfileForm(request.POST, instance=student)
        if profile_form.is_valid():
            student_profile = profile_form.save(commit=False)
            student_profile.profile_completed = True
            student_profile.save()
            messages.success(request, 'Student profile updated successfully!')
            return redirect('student_detail', student_id=student.id)
    else:
        profile_form = StudentProfileForm(instance=student)
    
    subjects = StudentSubject.objects.filter(student=student).select_related('subject')
    results = Result.objects.filter(student=student).select_related('subject')
    attendance_records = Attendance.objects.filter(student=student).select_related('subject')
    
    context = {
        'student': student,
        'profile_form': profile_form,
        'subjects': subjects,
        'results': results,
        'attendance_records': attendance_records,
        'all_subjects': Subject.objects.all(),
    }
    return render(request, 'admin_panel/student_detail.html', context)

@user_passes_test(is_staff_or_superuser)
def add_subject_to_student(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(StudentProfile, id=student_id)
        subject_id = request.POST.get('subject_id')
        subject = get_object_or_404(Subject, id=subject_id)
        
        StudentSubject.objects.get_or_create(student=student, subject=subject)
        messages.success(request, f'Subject {subject.name} added to student.')
    
    return redirect('student_detail', student_id=student_id)

@user_passes_test(is_staff_or_superuser)
def add_result(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(StudentProfile, id=student_id)
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            result.student = student
            result.save()
            messages.success(request, 'Result added successfully!')
    
    return redirect('student_detail', student_id=student_id)

@user_passes_test(is_staff_or_superuser)
def add_attendance(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(StudentProfile, id=student_id)
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.student = student
            attendance.save()
            messages.success(request, 'Attendance added successfully!')
    
    return redirect('student_detail', student_id=student_id)

@user_passes_test(is_staff_or_superuser)
def delete_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    user = student.user
    user.delete()  # This will also delete the StudentProfile due to cascade
    messages.success(request, 'Student deleted successfully!')
    return redirect('student_list')