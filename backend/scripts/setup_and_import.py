import os
import subprocess
import csv
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PROJECT_BACKEND_PACKAGE_PATH = os.path.join(PROJECT_ROOT, 'backend')

def create_database_if_missing(dbname, user, password, host, port):
    try:
        import psycopg
        conn = psycopg.connect(dbname='postgres', user=user, password=password, host=host, port=port)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE {dbname}")
                print(f"Created database {dbname}")
            else:
                print(f"Database {dbname} already exists")
        conn.close()
    except Exception as e:
        print('Error creating database:', e)
        raise

def run_migrations():
    subprocess.check_call([sys.executable, 'manage.py', 'migrate'], cwd=os.path.join(PROJECT_ROOT, 'backend'))

def import_students(csv_path):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    # Ensure the backend package folder is on sys.path so `backend.settings` can be imported
    if PROJECT_BACKEND_PACKAGE_PATH not in sys.path:
        sys.path.insert(0, PROJECT_BACKEND_PACKAGE_PATH)
    import django
    django.setup()
    from rfid.models import Student

    created = 0
    updated = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            student_id = row.get('student_id')
            if not student_id:
                continue
            defaults = {
                'name': row.get('name') or '',
                'program': row.get('program') or '',
                'year': row.get('year') or '',
                'section': row.get('section') or '',
                'rfid_uid': row.get('rfid_uid') or '',
            }
            obj, created_flag = Student.objects.update_or_create(student_id=student_id, defaults=defaults)
            if created_flag:
                created += 1
            else:
                updated += 1
    print(f"Import finished: {created} created, {updated} updated")

def main():
    DB = {
        'NAME': 'rfid_student',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
    csv_path = os.path.join(PROJECT_ROOT, 'Student-2026-02-16.csv')
    create_database_if_missing(DB['NAME'], DB['USER'], DB['PASSWORD'], DB['HOST'], DB['PORT'])
    run_migrations()
    import_students(csv_path)

if __name__ == '__main__':
    main()
