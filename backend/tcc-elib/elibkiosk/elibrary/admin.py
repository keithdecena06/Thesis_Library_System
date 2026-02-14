from django.contrib import admin
from .models import Program, Book, Thesis, RFIDUser, RFIDLog


# BASIC MODELS
admin.site.register(Program)
admin.site.register(Book)
admin.site.register(Thesis)


# RFID USER
@admin.register(RFIDUser)
class RFIDUserAdmin(admin.ModelAdmin):
    list_display = (
        "id_number",
        "full_name",
        "role",
        "program",
        "year_level",
        "section",
        "is_active",
    )
    search_fields = ("id_number", "full_name", "rfid_uid")
    list_filter = ("role", "program", "year_level", "is_active")


# RFID LOGS
@admin.register(RFIDLog)
class RFIDLogAdmin(admin.ModelAdmin):
    list_display = ("get_uid", "get_id_number", "scanned_at")
    search_fields = ("userrfid_uid", "userid_number")
    ordering = ("-scanned_at",)

    def get_uid(self, obj):
        return obj.user.rfid_uid
    get_uid.short_description = "RFID UID"

    def get_id_number(self, obj):
        return obj.user.id_number
    get_id_number.short_description = "ID Number"