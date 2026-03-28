import pandas as pd
from django.core.management.base import BaseCommand
from elibrary.models import Program, Book, Thesis


class Command(BaseCommand):
    help = "Import books or theses from Excel file (safe, no duplicates)"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        file_path = options["file_path"]
        df = pd.read_excel(file_path)

        # normalize column names
        df.columns = df.columns.str.lower().str.strip()
        columns = set(df.columns)

        # ======================
        # BOOKS EXCEL (WITH YEAR LEVEL)
        # ======================
        if {
            "program_code",
            "title",
            "author",
            "year_published",
            "year_level",
            "category",
        }.issubset(columns):
            self.import_books(df)

        # ======================
        # THESES EXCEL
        # ======================
        elif {
            "program_code",
            "title",
            "student_name",
            "year",
            "category",
        }.issubset(columns):
            self.import_theses(df)

        else:
            self.stderr.write(
                self.style.ERROR(
                    "❌ Unknown Excel format. Check column names."
                )
            )

    # ======================
    # IMPORT BOOKS (SAFE + YEAR LEVEL + CLEAN CATEGORY)
    # ======================
    def import_books(self, df):
        for _, row in df.iterrows():
            try:
                program = Program.objects.get(code=row["program_code"])
            except Program.DoesNotExist:
                self.stderr.write(
                    self.style.WARNING(
                        f"⚠️ Program code not found: {row['program_code']}"
                    )
                )
                continue

            # 🔹 CLEAN CATEGORY LOGIC
            raw_category = str(row["category"])
            main_category = raw_category.split(",")[0].strip()

            Book.objects.update_or_create(
                title=row["title"],
                author=row["author"],
                program=program,
                defaults={
                    "year_published": int(row["year_published"]),
                    "year_level": int(row["year_level"]),
                    "category": main_category,
                }
            )

        self.stdout.write(
            self.style.SUCCESS("✅ Books imported / updated successfully")
        )

    # ======================
    # IMPORT THESES (SAFE)
    # ======================
    def import_theses(self, df):
        for _, row in df.iterrows():
            try:
                program = Program.objects.get(code=row["program_code"])
            except Program.DoesNotExist:
                self.stderr.write(
                    self.style.WARNING(
                        f"⚠️ Program code not found: {row['program_code']}"
                    )
                )
                continue

            Thesis.objects.update_or_create(
                title=row["title"],
                student_name=row["student_name"],
                program=program,
                defaults={
                    "year": int(row["year"]),
                    "category": row["category"],
                }
            )

        self.stdout.write(
            self.style.SUCCESS("✅ Theses imported / updated successfully")
        )