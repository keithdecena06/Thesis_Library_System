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

@admin.register(AttendanceLog)
class AttendanceLogAdmin(ImportExportModelAdmin):
    resource_class = AttendanceLogResource
    list_display = ('student', 'action', 'timestamp', 'activity', 'program')
    list_filter = ('action', 'timestamp', 'activity', 'program')
