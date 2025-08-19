from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(default=3)

    def __str__(self):
        return f"{self.code} - {self.name}"

class StudentSubject(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    enrolled_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.name}"

class Result(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+ (90-100)'),
        ('A', 'A (80-89)'),
        ('B+', 'B+ (70-79)'),
        ('B', 'B (60-69)'),
        ('C+', 'C+ (50-59)'),
        ('C', 'C (40-49)'),
        ('F', 'F (Below 40)'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    total_marks = models.IntegerField(default=100)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    exam_date = models.DateField()
    exam_type = models.CharField(max_length=50, default='Final Exam')

    class Meta:
        unique_together = ('student', 'subject', 'exam_type')

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.code} - {self.grade}"

class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_classes = models.IntegerField(validators=[MinValueValidator(1)])
    classes_attended = models.IntegerField(validators=[MinValueValidator(0)])
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    month = models.CharField(max_length=20)
    year = models.IntegerField()

    class Meta:
        unique_together = ('student', 'subject', 'month', 'year')

    def save(self, *args, **kwargs):
        if self.classes_attended and self.total_classes:
            self.attendance_percentage = (self.classes_attended / self.total_classes) * 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.code} - {self.attendance_percentage}%"