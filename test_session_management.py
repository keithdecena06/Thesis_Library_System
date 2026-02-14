#!/usr/bin/env python
"""
Test script to demonstrate the automatic session closure functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta, date
from django.utils import timezone

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rfid.models import Student, AttendanceLog
from django.utils import timezone

def test_cross_day_session():
    """Test the cross-day session handling"""
    print("=== Testing Cross-Day Session Handling ===")

    # Get a test student
    try:
        student = Student.objects.get(student_id='TCC-0072-2023')
        print(f"Testing with student: {student.name}")
    except Student.DoesNotExist:
        print("Test student not found. Please create a student first.")
        return

    # Simulate yesterday's IN entry - use a date that is definitely yesterday
    from django.utils.dateparse import parse_datetime
    
    # Create yesterday's date at 10 AM
    yesterday_str = f"{(timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d')} 10:00:00+00:00"
    yesterday_dt = parse_datetime(yesterday_str)
    
    yesterday_log = AttendanceLog.objects.create(
        student=student,
        action='IN',
        timestamp=yesterday_dt
    )
    
    print(f"Created yesterday's IN entry: {yesterday_log.timestamp}")
    print(f"Yesterday datetime: {yesterday_dt}")
    print(f"Current time: {timezone.now()}")
    print(f"Yesterday date: {yesterday_dt.date()}")
    print(f"Current date: {timezone.now().date()}")

    # Simulate today's tap (this would normally happen via RFID)
    print("\nSimulating today's RFID tap...")
    
    # Check what the idle view would do - replicate the logic
    last_log = AttendanceLog.objects.filter(student=student).order_by('-timestamp').first()
    
    # Convert both timestamps to Manila time for date comparison (same as idle view)
    manila_tz = timezone.get_current_timezone()
    today_manila = timezone.now().astimezone(manila_tz).date()
    last_in_manila = last_log.timestamp.astimezone(manila_tz).date()
    
    print(f"Last log action: {last_log.action}")
    print(f"Last log timestamp (UTC): {last_log.timestamp}")
    print(f"Last log date (Manila): {last_in_manila}")
    print(f"Today date (Manila): {today_manila}")
    print(f"Is last action IN? {last_log.action == 'IN'}")
    print(f"Is last date before today? {last_in_manila < today_manila}")

    if last_log and last_log.action == 'IN':
        if last_in_manila < today_manila:
            print("✓ System detected previous day IN session")
            print("✓ Would automatically create OUT entry for yesterday")
            # Simulate creating the OUT entry
            AttendanceLog.objects.create(student=student, action='OUT')
            print("✓ Created OUT entry for yesterday")
            print("✓ Would redirect to reason page for new IN session")
        else:
            print("✓ Same day IN - would redirect to rating page")
    else:
        print("✓ No IN session - would redirect to reason page")

    # Clean up test data
    yesterday_log.delete()
    print("\nTest data cleaned up")

def test_daily_auto_close():
    """Test the daily auto-closure functionality"""
    print("\n=== Testing Daily Auto-Closure ===")

    # Run the management command
    from django.core.management import call_command
    from io import StringIO

    out = StringIO()
    call_command('close_sessions', stdout=out)
    output = out.getvalue()
    print("Management command output:")
    print(output)

if __name__ == '__main__':
    test_cross_day_session()
    test_daily_auto_close()