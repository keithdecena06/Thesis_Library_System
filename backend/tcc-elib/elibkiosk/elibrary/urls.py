from django.urls import path
from . import views

app_name = "elibrary"

urlpatterns = [
    # HOME
    path("", views.home, name="home"),

    # LANDING PAGES
    path("catalog/programs/", views.programs, name="programs"),
    path("catalog/theses/", views.theses, name="theses"),
    path("idle/", views.idle, name="idle"),

    # AUTH / USER
    path("record/", views.record_book, name="record_book"),
    path("account/", views.account, name="account"),

    # PROGRAM → BOOK LIST
    path(
        "catalog/programs/<str:program_code>/",
        views.program_books,
        name="program_books"
    ),

    # PROGRAM → THESIS LIST
    path(
        "catalog/theses/<str:program_code>/",
        views.thesis_list,
        name="thesis_list"
    ),

    # SEARCH
    path("search/", views.search_results, name="search_results"),
    path("api/search/", views.api_search, name="api_search"),

    # RFID APIs
    path("api/rfid/", views.rfid_api, name="rfid_api"),
    path("api/rfid/tap/", views.rfid_tap, name="rfid_tap"),
    path("api/last-scan/", views.last_scan, name="last_scan"),
    path("api/consume-scan/", views.consume_scan),  
    path("api/logout/", views.logout_user),
    path("api/library-action/", views.library_action),
]