from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Student, AttendanceLog
from django.utils import timezone
from datetime import datetime, date
from django.views.decorators.csrf import csrf_exempt
import json

# Global variable to store latest RFID scan (in production, use Redis or database)
latest_scan = None
last_scan_time = None

def get_greeting():
    now = datetime.now().hour
    if 5 <= now < 12:
        return "Good morning"
    elif 12 <= now < 17:
        return "Good afternoon"
    else:
        return "Good evening"

@csrf_exempt
def idle(request):
    if request.method == 'POST':
        rfid_uid = request.POST.get('rfid_uid')
        if rfid_uid:
            try:
                student = Student.objects.get(rfid_uid=rfid_uid)
                # Check if currently IN
                last_log = AttendanceLog.objects.filter(student=student).order_by('-timestamp').first()
                if last_log and last_log.action == 'IN':
                    # Check if the IN was from a previous day
                    # Convert both timestamps to Manila time for date comparison
                    manila_tz = timezone.get_current_timezone()
                    today_manila = timezone.now().astimezone(manila_tz).date()
                    last_in_manila = last_log.timestamp.astimezone(manila_tz).date()
                    
                    if last_in_manila < today_manila:
                        # Previous day IN without OUT - auto close it and start new session
                        program = student.program
                        AttendanceLog.objects.create(student=student, action='OUT', program=program)
                        # Now proceed with new IN session
                        return redirect('reason', student_id=student.student_id)
                    else:
                        # Same day IN - go to logout (rating page)
                        return redirect('rating', student_id=student.student_id)
                else:
                    # OUT or no previous logs - go to reason
                    return redirect('reason', student_id=student.student_id)
            except Student.DoesNotExist:
                return render(request, 'rfid/idle.html', {'error': 'Student not found'})
    return render(request, 'rfid/idle.html')

@csrf_exempt
def rfid_log(request):
    global latest_scan, last_scan_time
    if request.method == 'POST':
        # Check if this scan is too soon after the last one (prevent accidental rapid taps)
        current_time = timezone.now()
        if last_scan_time and (current_time - last_scan_time).seconds < 3:
            # Ignore rapid scans (less than 3 seconds apart)
            return JsonResponse({'status': 'ignored', 'message': 'Rapid scan ignored'})
        
        try:
            data = json.loads(request.body)
            rfid_uid = data.get('uid')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        if not rfid_uid:
            return JsonResponse({'error': 'No UID provided'}, status=400)
        
        try:
            student = Student.objects.get(rfid_uid=rfid_uid)
            # Check if currently IN
            last_log = AttendanceLog.objects.filter(student=student).order_by('-timestamp').first()
            if last_log and last_log.action == 'IN':
                # Check if the IN was from a previous day
                manila_tz = timezone.get_current_timezone()
                today_manila = timezone.now().astimezone(manila_tz).date()
                last_in_manila = last_log.timestamp.astimezone(manila_tz).date()
                
                if last_in_manila < today_manila:
                    # Previous day IN without OUT - auto close it and start new session
                    program = student.program
                    AttendanceLog.objects.create(student=student, action='OUT', program=program)
                    # Now proceed with new IN session
                    result = {
                        'status': 'success',
                        'action': 'login',
                        'student_id': student.student_id,
                        'redirect_url': f'/api/reason/{student.student_id}/'
                    }
                else:
                    # Same day IN - go to rating for logout
                    result = {
                        'status': 'success',
                        'action': 'logout',
                        'student_id': student.student_id,
                        'redirect_url': f'/api/rating/{student.student_id}/'
                    }
            else:
                # OUT or no previous logs - go to reason
                result = {
                    'status': 'success',
                    'action': 'login',
                    'student_id': student.student_id,
                    'redirect_url': f'/api/reason/{student.student_id}/'
                }
            
            # Store the latest scan for web app polling
            latest_scan = result
            last_scan_time = current_time
            return JsonResponse(result)
            
        except Student.DoesNotExist:
            result = {
                'status': 'error',
                'message': 'Student not found',
                'error': 'Student not found'
            }
            latest_scan = result
            last_scan_time = current_time
            return JsonResponse(result, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def check_rfid_scan(request):
    global latest_scan
    if request.method == 'GET':
        if latest_scan:
            # Return and clear the scan
            scan = latest_scan
            latest_scan = None
            return JsonResponse(scan)
        else:
            return JsonResponse({'status': 'no_scan'})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def reason(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        activity = request.POST.get('activity')
        if activity:
            AttendanceLog.objects.create(student=student, action='IN', activity=activity, program=student.program)
            return redirect('greetings', student_id=student.student_id)
    return render(request, 'rfid/reason.html', {'student': student})

def greetings(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    greeting = get_greeting()
    student_number = student.student_id
    entry_time = timezone.now()
    return render(request, 'rfid/greetings.html', {
        'student': student,
        'greeting': greeting,
        'student_number': student_number,
        'entry_time': entry_time
    })

def rating(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    # Don't automatically log out here - wait for card tap on idle page
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        # Create OUT entry when rating is submitted (during logout)
        last_log = AttendanceLog.objects.filter(student=student).order_by('-timestamp').first()
        if last_log and last_log.action == 'IN':
            AttendanceLog.objects.create(student=student, action='OUT')
        return redirect('thankyou')
    return render(request, 'rfid/rating.html', {'student': student})

def thankyou(request):
    return render(request, 'rfid/thankyou.html')
