@echo off
cd /d C:\Users\Keith\Desktop\smart_library
call .venv\Scripts\activate.bat
cd backend
python manage.py close_sessions
echo Session closure completed at %date% %time% >> C:\Users\Keith\Desktop\smart_library\session_closure.log