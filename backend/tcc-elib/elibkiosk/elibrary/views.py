from django.shortcuts import render, get_object_or_404, redirect
from .models import Program, Thesis, Book, RFIDUser, RFIDLog, LibraryAction
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from datetime import timedelta

LAST_RFID_USER_ID = None
COOLDOWN_SECONDS = 10  # adjust if gusto mo (anti-spam)

def home(request):
    return render(request, "kiosk/home.html")


def programs(request):
    return render(request, "catalog/programs.html")


def theses(request):
    return render(request, "catalog/theses.html")


def record_book(request):
    return render(request, "auth/record_book.html")

def program_books(request, program_code):
    program = get_object_or_404(Program, code=program_code)
    books = program.books.all().order_by("title")

    return render(
        request,
        "catalog/program_list.html",
        {
            "program": program,
            "books": books,
        }
    )

def thesis_list(request, program_code):
    if program_code == "best":
        theses = Thesis.objects.order_by("-year")
        program = None
    else:
        program = get_object_or_404(Program, code=program_code)
        theses = program.theses.all().order_by("-year")

    # UNIQUE YEARS FOR FILTER PILLS
    years = sorted({t.year for t in theses}, reverse=True)

    return render(
        request,
        "catalog/thesis_list.html",
        {
            "program": program,
            "theses": theses,
            "years": years,
        }
    )

def search_results(request):
    query = request.GET.get("q", "").strip()
    focus = request.GET.get("focus", "").strip()

    books = Book.objects.filter(
        Q(title__icontains=query) |
        Q(category__icontains=query)|
        Q(author__icontains=query)
    ).order_by("title")

    theses = Thesis.objects.filter(
        Q(title__icontains=query) |
        Q(category__icontains=query)|
        Q(student_name__icontains=query)
    ).order_by("title")

    return render(
        request,
        "catalog/search_results.html",
        {
            "query": query,
            "focus": focus,
            "books": books,
            "theses": theses,
        }
    )

def api_search(request):
    q = request.GET.get("q", "").strip()

    if len(q) < 2:
        return JsonResponse({"results": []})

    books = Book.objects.filter(
        Q(title__icontains=q) |
        Q(author__icontains=q) |
        Q(category__icontains=q)
    )

    theses = Thesis.objects.filter(
        Q(title__icontains=q) |
        Q(student_name__icontains=q) |
        Q(category__icontains=q)
    )

    results = []

    for b in books:
        results.append({
            "id": b.id,
            "title": b.title,
            "type": "Book",
            "meta": b.author or ""
        })

    for t in theses:
        results.append({
            "id": t.id,
            "title": t.title,
            "type": "Thesis",
            "meta": f"{t.student_name} • {t.year}"
        })

    return JsonResponse({"results": results})

@csrf_exempt
def rfid_tap(request):
    if request.method == "POST":
        data = json.loads(request.body)
        uid = data.get("uid")

        # TEMP: just log it
        print("RFID UID received:", uid)

        return JsonResponse({
            "status": "ok",
            "uid": uid
        })
    
@csrf_exempt
def rfid_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
        uid = data.get("uid")

        if not uid:
            return JsonResponse({"error": "UID missing"}, status=400)

        try:
            user = RFIDUser.objects.get(rfid_uid=uid, is_active=True)
        except RFIDUser.DoesNotExist:
            return JsonResponse({
                "status": "unregistered",
                "uid": uid
            })

        # 🔒 COOLDOWN CHECK
        last_log = (
            RFIDLog.objects
            .filter(user=user)
            .order_by("-scanned_at")
            .first()
        )

        if last_log:
            diff = timezone.now() - last_log.scanned_at
            if diff < timedelta(seconds=COOLDOWN_SECONDS):
                return JsonResponse({
                    "status": "cooldown",
                    "seconds_left": COOLDOWN_SECONDS - int(diff.total_seconds())
                })

        # ✅ LOG THE SCAN
        RFIDLog.objects.create(user=user)

        return JsonResponse({
            "status": "success",
            "user_id": user.id,
            "id_number": user.id_number
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def account(request):
    user_id = request.session.get("rfid_user_id")
    if not user_id:
        return render(request, "auth/account_waiting.html")

    user = get_object_or_404(RFIDUser, id=user_id)

    actions = (
        LibraryAction.objects
        .filter(user=user)
        .order_by("-created_at")
    )

    enriched = []

    for a in actions:
        item = None
        title = ""
        meta = ""

        if a.content_type == "book":
            item = Book.objects.filter(id=a.content_id).first()
            if item:
                title = item.title
                meta = item.author

        elif a.content_type == "thesis":
            item = Thesis.objects.filter(id=a.content_id).first()
            if item:
                title = item.title
                meta = item.student_name

        enriched.append({
            "action": a.action,              # recorded / saved
            "content_type": a.content_type,  # book / thesis
            "title": title,
            "meta": meta,
            "created_at": a.created_at,
        })

    return render(request, "auth/account.html", {
        "user": user,
        "activities": enriched,
    })

def last_scan(request):
    log = (
        RFIDLog.objects
        .filter(consumed=False)
        .order_by("-scanned_at")
        .first()
    )

    if not log:
        return JsonResponse({"found": False})

    return JsonResponse({
        "found": True,
        "log_id": log.id,
        "user_id": log.user.id
    })

@csrf_exempt
def consume_scan(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)
    log_id = data.get("log_id")

    try:
        log = RFIDLog.objects.get(id=log_id)

        # ✅ SET SESSION HERE
        request.session["rfid_user_id"] = log.user.id
        request.session["last_activity"] = timezone.now().timestamp()

        log.consumed = True
        log.save()

        return JsonResponse({
            "status": "ok",
            "user_id": log.user.id
        })

    except RFIDLog.DoesNotExist:
        return JsonResponse({"error": "Log not found"}, status=404)

def idle(request):
    return render(request, "kiosk/idle.html")

def get_logged_user(request):
    uid = request.session.get("rfid_user_id")
    if not uid:
        return None
    return RFIDUser.objects.filter(id=uid).first()

def record_book(request):
    # 1️⃣ priority: session user
    session_user_id = request.session.get("rfid_user_id")
    query_user_id = request.GET.get("user")

    user_id = query_user_id or session_user_id

    if not user_id:
        # walang session, walang query → balik home (or idle)
        return redirect("elibrary:home")

    user = get_object_or_404(RFIDUser, id=user_id)

    return render(request, "auth/record_book.html", {
        "user": user
    })

@csrf_exempt
def logout_user(request):
    request.session.flush()  # 🔥 remove RFID session
    return JsonResponse({"ok": True})

@csrf_exempt
def library_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    user_id = request.session.get("rfid_user_id")
    if not user_id:
        return JsonResponse({"error": "Not logged in"}, status=401)

    data = json.loads(request.body)

    content_type = data.get("content_type")   # "book" | "thesis"
    content_id = data.get("content_id")
    action = data.get("action")               # "recorded" | "saved"

    if action not in ["recorded", "saved"]:
        return JsonResponse({"error": "Invalid action"}, status=400)

    if content_type not in ["book", "thesis"]:
        return JsonResponse({"error": "Invalid content type"}, status=400)

    LibraryAction.objects.create(
        user_id=user_id,
        content_type=content_type,
        content_id=content_id,
        action=action
    )

    return JsonResponse({"status": "ok"})