from django.core.management.base import BaseCommand
from django.utils import timezone
from rfid.models import AttendanceLog, Student
from datetime import datetime, date

class Command(BaseCommand):
    help = 'Automatically close all open IN sessions at 6 PM daily'

    def handle(self, *args, **options):
        # Get current date
        today = date.today()
        
        # Find all students who have IN actions without corresponding OUT
        open_sessions = []
        
        # Get all students
        students = Student.objects.all()
        
        for student in students:
            # Get the last log for this student
            last_log = AttendanceLog.objects.filter(student=student).order_by('-timestamp').first()
            
            # If last action is IN and it's from today, mark as open session
            if last_log and last_log.action == 'IN' and last_log.timestamp.date() == today:
                open_sessions.append(student)
        
        # Create OUT entries for all open sessions
        for student in open_sessions:
            AttendanceLog.objects.create(student=student, action='OUT')
            self.stdout.write(
                self.style.SUCCESS(f'Automatically closed session for {student.name} ({student.student_id})')
            )
        
        if open_sessions:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully closed {len(open_sessions)} open sessions at 6 PM')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No open sessions found to close')
            )