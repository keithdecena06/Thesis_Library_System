from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
import pandas as pd

from .models import Program, Book, Thesis, RFIDUser, RFIDLog


# =========================
# PROGRAM ADMIN
# =========================
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("code",)


# =========================
# THESIS ADMIN
# =========================
@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ("title", "student_name", "program", "year", "category", "is_best")
    search_fields = ("title", "student_name", "program__code", "program__name", "category")
    list_filter = ("program", "year", "category", "is_best")
    ordering = ("-year", "title")
    change_list_template = "admin/import_excel.html"
    actions = ["delete_all_theses"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel),
                name="thesis_import_excel",
            ),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        if request.method == "POST":
            file = request.FILES.get("file")

            if not file:
                messages.error(request, "❌ No file uploaded.")
                return redirect("..")

            try:
                df = pd.read_excel(file, engine="openpyxl")
            except Exception as e:
                messages.error(request, f"❌ Invalid file: {e}")
                return redirect("..")

            df.columns = df.columns.str.lower().str.strip()

            required_columns = {
                "program_code",
                "title",
                "student_name",
                "year",
                "category",
            }

            if not required_columns.issubset(df.columns):
                messages.error(
                    request,
                    f"❌ Missing required columns. Required: {', '.join(required_columns)}"
                )
                return redirect("..")

            imported_count = 0
            skipped_count = 0

            for _, row in df.iterrows():
                try:
                    program = Program.objects.filter(code=str(row["program_code"]).strip()).first()
                    if not program:
                        skipped_count += 1
                        continue

                    Thesis.objects.update_or_create(
                        title=str(row["title"]).strip(),
                        student_name=str(row["student_name"]).strip(),
                        program=program,
                        defaults={
                            "year": int(row["year"]),
                            "category": str(row["category"]).strip(),
                        }
                    )
                    imported_count += 1

                except Exception:
                    skipped_count += 1

            messages.success(
                request,
                f"✅ Theses imported successfully. Imported/Updated: {imported_count}, Skipped: {skipped_count}"
            )
            return redirect("..")

        return render(request, "admin/import_form.html")

    def delete_all_theses(self, request, queryset):
        if not queryset.exists():
            count = Thesis.objects.count()
            Thesis.objects.all().delete()
            self.message_user(request, f"💀 {count} theses deleted (no selection needed)")
            return

        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"💀 {count} selected theses deleted")

    delete_all_theses.short_description = "Delete all theses"


# =========================
# BOOK ADMIN
# =========================
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "program", "year_published", "year_level", "category")
    search_fields = ("title", "author", "program__code", "program__name", "category")
    list_filter = ("program", "year_level", "category", "year_published")
    ordering = ("title",)
    change_list_template = "admin/import_excel.html"
    actions = ["delete_all_books"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel),
                name="book_import_excel",
            ),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        if request.method == "POST":
            file = request.FILES.get("file")

            if not file:
                messages.error(request, "❌ No file uploaded.")
                return redirect("..")

            try:
                df = pd.read_excel(file, engine="openpyxl")
            except Exception as e:
                messages.error(request, f"❌ Invalid file: {e}")
                return redirect("..")

            df.columns = df.columns.str.lower().str.strip()

            required_columns = {
                "program_code",
                "title",
                "author",
                "year_published",
                "year_level",
                "category",
            }

            if not required_columns.issubset(df.columns):
                messages.error(
                    request,
                    f"❌ Missing required columns. Required: {', '.join(required_columns)}"
                )
                return redirect("..")

            imported_count = 0
            skipped_count = 0

            for _, row in df.iterrows():
                try:
                    program = Program.objects.filter(code=str(row["program_code"]).strip()).first()
                    if not program:
                        skipped_count += 1
                        continue

                    Book.objects.update_or_create(
                        title=str(row["title"]).strip(),
                        author=str(row["author"]).strip(),
                        program=program,
                        defaults={
                            "year_published": int(row["year_published"]),
                            "year_level": int(row["year_level"]),
                            "category": str(row["category"]).split(",")[0].strip(),
                        }
                    )
                    imported_count += 1

                except Exception:
                    skipped_count += 1

            messages.success(
                request,
                f"✅ Books imported successfully. Imported/Updated: {imported_count}, Skipped: {skipped_count}"
            )
            return redirect("..")

        return render(request, "admin/import_form.html")

    def delete_all_books(self, request, queryset):
        if not queryset.exists():
            count = Book.objects.count()
            Book.objects.all().delete()
            self.message_user(request, f"💀 {count} books deleted (no selection needed)")
            return

        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"💀 {count} selected books deleted")

    delete_all_books.short_description = "Delete all books"


# =========================
# RFID USER ADMIN
# =========================
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
    search_fields = (
        "id_number",
        "full_name",
        "rfid_uid",
        "program__code",
        "program__name",
        "section",
    )
    list_filter = ("role", "program", "year_level", "is_active")
    ordering = ("id_number",)
    change_list_template = "admin/import_excel.html"
    actions = ["delete_all_rfid_users"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel),
                name="rfiduser_import_excel",
            ),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        if request.method == "POST":
            file = request.FILES.get("file")

            if not file:
                messages.error(request, "❌ No file uploaded.")
                return redirect("..")

            try:
                df = pd.read_excel(file, engine="openpyxl")
            except Exception as e:
                messages.error(request, f"❌ Invalid file: {e}")
                return redirect("..")

            df.columns = df.columns.str.lower().str.strip()

            required_columns = {
                "id_number",
                "full_name",
                "rfid_uid",
                "role",
                "program_code",
                "year_level",
                "section",
                "is_active",
            }

            if not required_columns.issubset(df.columns):
                messages.error(
                    request,
                    f"❌ Missing required columns. Required: {', '.join(required_columns)}"
                )
                return redirect("..")

            imported_count = 0
            skipped_count = 0

            for _, row in df.iterrows():
                try:
                    program = None
                    if pd.notna(row["program_code"]):
                        program = Program.objects.filter(
                            code=str(row["program_code"]).strip()
                        ).first()

                    is_active_value = str(row["is_active"]).strip().lower()
                    is_active = is_active_value in ["true", "1", "yes", "y"]

                    RFIDUser.objects.update_or_create(
                        id_number=str(row["id_number"]).strip(),
                        defaults={
                            "full_name": str(row["full_name"]).strip(),
                            "rfid_uid": str(row["rfid_uid"]).strip(),
                            "role": str(row["role"]).strip(),
                            "program": program,
                            "year_level": int(row["year_level"]) if pd.notna(row["year_level"]) else None,
                            "section": str(row["section"]).strip() if pd.notna(row["section"]) else "",
                            "is_active": is_active,
                        }
                    )
                    imported_count += 1

                except Exception:
                    skipped_count += 1

            messages.success(
                request,
                f"✅ RFID users imported successfully. Imported/Updated: {imported_count}, Skipped: {skipped_count}"
            )
            return redirect("..")

        return render(request, "admin/import_form.html")

    def delete_all_rfid_users(self, request, queryset):
        if not queryset.exists():
            count = RFIDUser.objects.count()
            RFIDUser.objects.all().delete()
            self.message_user(request, f"💀 {count} RFID users deleted (no selection needed)")
            return

        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"💀 {count} selected RFID users deleted")

    delete_all_rfid_users.short_description = "Delete all RFID users"


# =========================
# RFID LOGS ADMIN
# =========================
@admin.register(RFIDLog)
class RFIDLogAdmin(admin.ModelAdmin):
    list_display = ("get_uid", "get_id_number", "get_full_name", "scanned_at")
    search_fields = ("user__rfid_uid", "user__id_number", "user__full_name")
    list_filter = ("scanned_at",)
    ordering = ("-scanned_at",)

    def get_uid(self, obj):
        return obj.user.rfid_uid if obj.user else "-"
    get_uid.short_description = "RFID UID"

    def get_id_number(self, obj):
        return obj.user.id_number if obj.user else "-"
    get_id_number.short_description = "ID Number"

    def get_full_name(self, obj):
        return obj.user.full_name if obj.user else "-"
    get_full_name.short_description = "Full Name"