#!/usr/bin/env python
"""
Load sample student data from CSV
"""
import os
import sys
import django
import csv

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rfid.models import Student

def load_students():
    csv_file = os.path.join(os.path.dirname(__file__), 'sample_students.csv')
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            student, created = Student.objects.get_or_create(
                student_id=row['student_id'],
                defaults={
                    'name': row['name'],
                    'program_year_section': row['program_year_section'],
                    'rfid_uid': row['rfid_uid']
                }
            )
            if created:
                print(f"Created student: {student}")
            else:
                print(f"Student already exists: {student}")

if __name__ == '__main__':
    load_students()