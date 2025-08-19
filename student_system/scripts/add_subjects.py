from main.models import Subject

subjects_data = [
    {'name': 'Mathematics', 'code': 'MATH101', 'credits': 4},
    {'name': 'Physics', 'code': 'PHY101', 'credits': 3},
    {'name': 'Chemistry', 'code': 'CHEM101', 'credits': 3},
    {'name': 'Computer Science', 'code': 'CS101', 'credits': 4},
    {'name': 'English', 'code': 'ENG101', 'credits': 2},
]

for subject_data in subjects_data:
    Subject.objects.get_or_create(**subject_data)
