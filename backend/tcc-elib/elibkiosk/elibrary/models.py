from django.db import models
from django.utils import timezone


class Program(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    def str(self):
        return self.name

class Book(models.Model):
    YEAR_LEVEL_CHOICES = [
        (1, "1st Year"),
        (2, "2nd Year"),
        (3, "3rd Year"),
        (4, "4th Year"),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    year_published = models.IntegerField()
    year_level = models.IntegerField(choices=YEAR_LEVEL_CHOICES)
    category = models.CharField(max_length=100)

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="books"
    )

    def str(self):
        return self.title


class Thesis(models.Model):
    title = models.CharField(max_length=200)
    student_name = models.CharField(max_length=150)
    year = models.IntegerField()
    category = models.CharField(max_length=100)

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="theses"
    )

    def str(self):
        return self.title
    
class RFIDUser(models.Model):
    rfid_uid = models.CharField(max_length=50, unique=True)
    id_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)

    ROLE_CHOICES = [
        ("student", "Student"),
        ("faculty", "Faculty"),
        ("staff", "Staff"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    program = models.ForeignKey(
        "Program",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    year_level = models.IntegerField(null=True, blank=True)
    section = models.CharField(max_length=10, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.id_number


class RFIDLog(models.Model):
    user = models.ForeignKey(
        RFIDUser,
        on_delete=models.CASCADE,
        related_name="logs"
    )
    scanned_at = models.DateTimeField(default=timezone.now)
    consumed = models.BooleanField(default=False)

    def str(self):
        return f"{self.user.id_number} @ {self.scanned_at}"
    
class LibraryAction(models.Model):
    ACTION_CHOICES = [
        ("recorded", "Recorded"),
        ("saved", "Saved"),
    ]

    CONTENT_CHOICES = [
        ("book", "Book"),
        ("thesis", "Thesis"),
    ]

    user = models.ForeignKey(
        RFIDUser,
        on_delete=models.CASCADE,
        related_name="library_actions"
    )

    content_type = models.CharField(max_length=10, choices=CONTENT_CHOICES)
    content_id = models.PositiveIntegerField()
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.id_number} {self.action} {self.content_type} {self.content_id}"