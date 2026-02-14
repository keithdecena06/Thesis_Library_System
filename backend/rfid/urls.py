from django.urls import path
from . import views

urlpatterns = [
    # Kiosk UI routes
    path('', views.idle, name='idle'),
    path('rfid/', views.idle, name='idle'),

    # API endpoints (used by Arduino and client-side polling)
    path('api/rfid/', views.idle, name='api_idle'),
    path('api/rfid_log/', views.rfid_log, name='api_rfid_log'),
    path('api/bridge_rfid/', views.bridge_rfid, name='api_bridge_rfid'),
    path('api/check_rfid_scan/', views.check_rfid_scan, name='api_check_rfid_scan'),
    path('api/reason/<str:student_id>/', views.reason, name='api_reason'),
    path('api/greetings/<str:student_id>/', views.greetings, name='api_greetings'),
    path('api/rating/<str:student_id>/', views.rating, name='api_rating'),
    path('api/thankyou/', views.thankyou, name='api_thankyou'),

    # Backwards-compatible non-API routes
    path('rfid_log/', views.rfid_log, name='rfid_log'),
    path('check_rfid_scan/', views.check_rfid_scan, name='check_rfid_scan'),
    path('reason/<str:student_id>/', views.reason, name='reason'),
    path('greetings/<str:student_id>/', views.greetings, name='greetings'),
    path('rating/<str:student_id>/', views.rating, name='rating'),
    path('thankyou/', views.thankyou, name='thankyou'),
]
