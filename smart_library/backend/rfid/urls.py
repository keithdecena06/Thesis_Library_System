from django.urls import path
from . import views

urlpatterns = [
    path('rfid/', views.idle, name='idle'),
    path('rfid_log/', views.rfid_log, name='rfid_log'),
    path('check_rfid_scan/', views.check_rfid_scan, name='check_rfid_scan'),
    path('reason/<str:student_id>/', views.reason, name='reason'),
    path('greetings/<str:student_id>/', views.greetings, name='greetings'),
    path('rating/<str:student_id>/', views.rating, name='rating'),
    path('thankyou/', views.thankyou, name='thankyou'),
]
