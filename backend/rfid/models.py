from django.db import models

# Create your models here.

PROGRAM_CHOICES = [
    ('BSMA', 'BSMA'),
    ('BSCPE', 'BSCPE'),
    ('BTVTED', 'BTVTED'),
    ('BSE', 'BSE'),
    ('BPA', 'BPA'),
]

class Student(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    program = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    year = models.CharField(max_length=10)
    section = models.CharField(max_length=10)
    rfid_uid = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class AttendanceLog(models.Model):
    ACTION_CHOICES = [
        ('IN', 'In'),
        ('OUT', 'Out'),
    ]
    ACTIVITY_CHOICES = [
        ('Borrowing', 'Borrowing'),
        ('Reading', 'Reading'),
        ('Facility', 'Facility'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    action = models.CharField(max_length=3, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, null=True, blank=True)
    program = models.CharField(max_length=10, choices=PROGRAM_CHOICES, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.action} at {self.timestamp}"
