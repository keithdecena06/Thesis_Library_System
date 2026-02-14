from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Student, AttendanceLog

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('student_id', 'name', 'program', 'year', 'section', 'rfid_uid')
        import_id_fields = ('student_id',)  # Use student_id as the identifier for imports

class AttendanceLogResource(resources.ModelResource):
    class Meta:
        model = AttendanceLog

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('student_id', 'name', 'program', 'year', 'section', 'rfid_uid')

class MonthYearListFilter(admin.SimpleListFilter):
    title = 'Month & Year'
    parameter_name = 'month_year'

    def lookups(self, request, model_admin):
        # Provide month-year combinations that exist in the data
        months = model_admin.model.objects.dates('timestamp', 'month')
        return [(m.strftime('%Y-%m'), m.strftime('%B %Y')) for m in months]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            year, month = value.split('-')
            return queryset.filter(timestamp__year=int(year), timestamp__month=int(month))
        return queryset

@admin.register(AttendanceLog)
class AttendanceLogAdmin(ImportExportModelAdmin):
    resource_class = AttendanceLogResource
    list_display = ('student', 'action', 'timestamp', 'activity', 'program', 'rating')
    list_filter = ('action', MonthYearListFilter, 'activity', 'program', 'rating')
