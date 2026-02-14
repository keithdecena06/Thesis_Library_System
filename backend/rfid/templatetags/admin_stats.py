from django import template
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Avg

from rfid.models import AttendanceLog, Student

from datetime import datetime, time

register = template.Library()


@register.inclusion_tag('admin/admin_stats.html', takes_context=True)
def library_stats(context):
    # Count students whose last attendance action is IN
    latest_action = AttendanceLog.objects.filter(student=OuterRef('pk')).order_by('-timestamp').values('action')[:1]
    in_count = Student.objects.annotate(last_action=Subquery(latest_action)).filter(last_action='IN').count()

    # Today's date in local timezone
    today = timezone.localdate()

    # Compute time window 08:00 to 19:00 in current timezone
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(today, time(8, 0)), timezone=tz)
    end_dt = timezone.make_aware(datetime.combine(today, time(19, 0)), timezone=tz)

    visits_8_19 = AttendanceLog.objects.filter(timestamp__gte=start_dt, timestamp__lte=end_dt, action='IN').count()

    # Keep full-day count as well for backward compatibility
    todays_visits = AttendanceLog.objects.filter(timestamp__date=today, action='IN').count()

    # Average rating for today (all ratings submitted on OUT entries)
    avg_rating_qs = AttendanceLog.objects.filter(timestamp__date=today, rating__isnull=False).aggregate(avg=Avg('rating'))
    avg_rating = avg_rating_qs.get('avg')

    return {
        'in_count': in_count,
        'todays_visits': todays_visits,
        'visits_8_19': visits_8_19,
        'avg_rating': avg_rating,
    }