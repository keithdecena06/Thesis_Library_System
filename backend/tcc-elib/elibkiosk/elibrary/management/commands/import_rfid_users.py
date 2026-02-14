import pandas as pd
from django.core.management.base import BaseCommand
from elibrary.models import RFIDUser, Program


class Command(BaseCommand):
    help = "Import RFID users from Excel file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        file_path = options["file_path"]
        df = pd.read_excel(file_path)

        df.columns = df.columns.str.lower().str.strip()

        required = {
            "rfid_uid",
            "id_number",
            "full_name",
            "role",
        }

        if not required.issubset(df.columns):
            self.stderr.write(
                self.style.ERROR(
                    f"❌ Missing required columns: {required}"
                )
            )
            return

        for _, row in df.iterrows():
            program = None
            if "program_code" in df.columns and pd.notna(row.get("program_code")):
                program = Program.objects.filter(
                    code=row["program_code"]
                ).first()

            RFIDUser.objects.update_or_create(
                rfid_uid=row["rfid_uid"],
                defaults={
                    "id_number": row["id_number"],
                    "full_name": row["full_name"],
                    "role": row["role"],
                    "program": program,
                    "year_level": row.get("year_level"),
                    "section": row.get("section", ""),
                    "is_active": True,
                }
            )

        self.stdout.write(
            self.style.SUCCESS("✅ RFID users imported successfully")
        )