import logging
from datetime import date

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import StudentRegistrationForm, SecurityCreationForm, StudentProfileForm
from .models import User
from access_requests.models import AccessRequest
from visitor_cards.models import VisitorCard, CardTransaction

logger = logging.getLogger(__name__)


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = StudentRegistrationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user

    if user.role == "ADMIN":
        today = timezone.localdate()

        # Awal bulan ini
        current_month = today.replace(day=1)

        # Awal periode grafik: 5 bulan sebelum bulan ini
        first_chart_month = current_month
        for _ in range(5):
            first_chart_month = (
                first_chart_month.replace(day=1)
            )
            if first_chart_month.month == 1:
                first_chart_month = first_chart_month.replace(
                    year=first_chart_month.year - 1,
                    month=12,
                )
            else:
                first_chart_month = first_chart_month.replace(
                    month=first_chart_month.month - 1
                )

        # Jumlah peminjaman per bulan
        monthly_borrowing = (
            CardTransaction.objects.filter(
                borrowed_at__date__gte=first_chart_month,
                borrowed_at__date__lte=today,
            )
            .annotate(month=TruncMonth("borrowed_at"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )

        borrowing_by_month = {
            (item["month"].year, item["month"].month): item["total"]
            for item in monthly_borrowing
        }

        # Membuat label dan data untuk 6 bulan terakhir,
        # termasuk bulan yang belum memiliki peminjaman.
        chart_labels = []
        chart_values = []

        month_cursor = first_chart_month

        for _ in range(6):
            month_key = (
                month_cursor.year,
                month_cursor.month,
            )

            chart_labels.append(
                month_cursor.strftime("%b %Y")
            )
            chart_values.append(
                borrowing_by_month.get(month_key, 0)
            )

            if month_cursor.month == 12:
                month_cursor = month_cursor.replace(
                    year=month_cursor.year + 1,
                    month=1,
                )
            else:
                month_cursor = month_cursor.replace(
                    month=month_cursor.month + 1
                )

        # Transaksi yang peminjamannya terjadi bulan ini
        monthly_transactions = CardTransaction.objects.filter(
            borrowed_at__date__gte=current_month,
            borrowed_at__date__lte=today,
        )

        context = {
            # Statistik mahasiswa dan petugas
            "total_students": User.objects.filter(
                role=User.Role.STUDENT
            ).count(),

            "active_students": User.objects.filter(
                role=User.Role.STUDENT,
                is_blocked=False,
            ).count(),

            "blocked_students": User.objects.filter(
                role=User.Role.STUDENT,
                is_blocked=True,
            ).count(),

            "total_security": User.objects.filter(
                role=User.Role.SECURITY
            ).count(),

            # Statistik permintaan akses
            "total_access_requests": AccessRequest.objects.count(),

            "pending_requests": AccessRequest.objects.filter(
                status=AccessRequest.Status.PENDING
            ).count(),

            # Statistik kartu
            "available_cards": VisitorCard.objects.filter(
                status=VisitorCard.Status.AVAILABLE
            ).count(),

            "borrowed_cards": CardTransaction.objects.filter(
                status=CardTransaction.Status.BORROWED
            ).count(),

            "blocked_cards": VisitorCard.objects.filter(
                status=VisitorCard.Status.BLOCKED
            ).count(),

            "overdue_transactions": CardTransaction.objects.filter(
                status=CardTransaction.Status.OVERDUE
            ).count(),

            # Ringkasan transaksi bulan ini
            "monthly_total_transactions": monthly_transactions.count(),

            "monthly_borrowed_transactions": monthly_transactions.filter(
                status=CardTransaction.Status.BORROWED
            ).count(),

            "monthly_returned_transactions": monthly_transactions.filter(
                status=CardTransaction.Status.RETURNED
            ).count(),

            "monthly_overdue_transactions": monthly_transactions.filter(
                status=CardTransaction.Status.OVERDUE
            ).count(),

            # Data grafik
            "borrowing_chart_labels": chart_labels,
            "borrowing_chart_values": chart_values,

            # Transaksi terbaru
            "recent_transactions": (
                CardTransaction.objects.select_related(
                    "student",
                    "card",
                    "access_request",
                ).order_by("-created_at")[:5]
            ),
        }

        return render(request, "admin_dashboard.html", context)

    elif user.role == "SECURITY":
        template = "security_dashboard.html"
    else:
        template = "student_dashboard.html"

    return render(request, template)

@login_required
def student_management(request):
    if request.user.role != User.Role.ADMIN:
        messages.error(request, "Kamu tidak memiliki akses ke halaman ini.")
        return redirect("dashboard")

    keyword = request.GET.get("q", "").strip()

    students = User.objects.filter(role=User.Role.STUDENT).order_by("username")

    if keyword:
        students = students.filter(
            Q(username__icontains=keyword)
            | Q(first_name__icontains=keyword)
            | Q(last_name__icontains=keyword)
            | Q(email__icontains=keyword)
            | Q(student_id__icontains=keyword)
        )

    context = {
        "students": students.order_by("username"),
        "keyword": keyword,
        "total_students": User.objects.filter(
            role=User.Role.STUDENT
        ).count(),
        "blocked_students": User.objects.filter(
            role=User.Role.STUDENT,
            is_blocked=True
        ).count(),
        "active_students": User.objects.filter(
            role=User.Role.STUDENT,
            is_blocked=False
        ).count(),
    }

    return render(request, "accounts/student_management.html", context)

@login_required
def toggle_student_block(request, user_id):
    if request.user.role != User.Role.ADMIN:
        messages.error(request, "Kamu tidak memiliki akses ke tindakan ini.")
        return redirect("dashboard")

    if request.method != "POST":
        return redirect("student_management")

    student = get_object_or_404(
        User,
        id=user_id,
        role=User.Role.STUDENT,
    )

    # Jangan membuka blokir otomatis akibat keterlambatan kartu.
    if student.is_blocked and student.overdue_blocked:
        messages.error(
            request,
            f"Akun {student.username} diblokir karena keterlambatan "
            "pengembalian kartu. Selesaikan masalah kartu terlebih dahulu.",
        )
        return redirect("student_management")

    student.is_blocked = not student.is_blocked
    student.save(update_fields=["is_blocked"])

    if student.is_blocked:
        messages.success(
            request,
            f"Akun mahasiswa {student.username} berhasil diblokir.",
        )
    else:
        messages.success(
            request,
            f"Akun mahasiswa {student.username} berhasil dibuka blokirnya.",
        )

    return redirect("student_management")

@login_required
def delete_student(request, user_id):
    if request.user.role != User.Role.ADMIN:
        messages.error(
            request,
            "Kamu tidak memiliki akses ke tindakan ini.",
        )
        return redirect("dashboard")

    if request.method != "POST":
        return redirect("student_management")

    student = get_object_or_404(
        User,
        id=user_id,
        role=User.Role.STUDENT,
    )

    # Cek peminjaman yang belum diselesaikan.
    active_transaction_exists = CardTransaction.objects.filter(
        student=student,
        status__in=[
            CardTransaction.Status.BORROWED,
            CardTransaction.Status.OVERDUE,
        ],
    ).exists()

    if active_transaction_exists:
        messages.error(
            request,
            f"Akun {student.username} tidak dapat dihapus karena "
            "masih memiliki peminjaman kartu yang belum diselesaikan. "
            "Pastikan kartu sudah dikembalikan terlebih dahulu.",
        )
        return redirect("student_management")

    # Periksa apakah masih ada riwayat transaksi.
    has_transaction_history = CardTransaction.objects.filter(
        student=student,
    ).exists()

    username = student.username

    if has_transaction_history:
        # Pertahankan riwayat transaksi dengan menonaktifkan akun.
        student.is_active = False
        student.save(update_fields=["is_active"])

        messages.success(
            request,
            f"Akun mahasiswa {username} dinonaktifkan karena "
            "memiliki riwayat transaksi yang harus dipertahankan. "
            "Akun tidak dapat digunakan untuk login.",
        )
    else:
        # Akun tanpa riwayat transaksi dapat dihapus.
        try:
            student.delete()

            messages.success(
                request,
                f"Akun mahasiswa {username} berhasil dihapus.",
            )

        except Exception:
            messages.error(
                request,
                f"Akun {username} tidak dapat dihapus karena "
                "masih memiliki data terkait yang harus dipertahankan.",
            )

    return redirect("student_management")

@login_required
def security_management(request):
    if request.user.role != User.Role.ADMIN:
        messages.error(
            request,
            "Kamu tidak memiliki akses ke halaman ini."
        )
        return redirect("dashboard")

    keyword = request.GET.get("q", "").strip()

    security_users = User.objects.filter(
        role=User.Role.SECURITY
    )

    if keyword:
        security_users = security_users.filter(
            Q(username__icontains=keyword)
            | Q(first_name__icontains=keyword)
            | Q(last_name__icontains=keyword)
            | Q(email__icontains=keyword)
        )

    context = {
        "security_users": security_users.order_by("username"),
        "keyword": keyword,
        "total_security": User.objects.filter(
            role=User.Role.SECURITY
        ).count(),
        "active_security": User.objects.filter(
            role=User.Role.SECURITY,
            is_blocked=False
        ).count(),
        "blocked_security": User.objects.filter(
            role=User.Role.SECURITY,
            is_blocked=True
        ).count(),
    }

    return render(
        request,
        "accounts/security_management.html",
        context
    )

@login_required
def create_security(request):
    if request.user.role != User.Role.ADMIN:
        messages.error(
            request,
            "Kamu tidak memiliki akses ke halaman ini."
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = SecurityCreationForm(request.POST)

        if form.is_valid():
            security_user = form.save()

            messages.success(
                request,
                f"Akun Security {security_user.username} berhasil dibuat."
            )
            return redirect("security_management")
    else:
        form = SecurityCreationForm()

    return render(
        request,
        "accounts/security_create.html",
        {"form": form}
    )

@login_required
def toggle_security_block(request, user_id):
    if request.user.role != User.Role.ADMIN:
        messages.error(
            request,
            "Kamu tidak memiliki akses ke tindakan ini."
        )
        return redirect("dashboard")

    if request.method != "POST":
        return redirect("security_management")

    security_user = get_object_or_404(
        User,
        id=user_id,
        role=User.Role.SECURITY
    )

    security_user.is_blocked = not security_user.is_blocked
    security_user.save(update_fields=["is_blocked"])

    if security_user.is_blocked:
        messages.success(
            request,
            f"Akun Security {security_user.username} berhasil diblokir."
        )
    else:
        messages.success(
            request,
            f"Akun Security {security_user.username} berhasil dibuka blokirnya."
        )

    return redirect("security_management")

@login_required
def edit_profile(request):
    if request.user.role != User.Role.STUDENT:
        messages.error(
            request,
            "Halaman ini hanya dapat diakses oleh mahasiswa."
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = StudentProfileForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Profil berhasil diperbarui."
            )
            return redirect("edit_profile")
    else:
        form = StudentProfileForm(instance=request.user)

    return render(
        request,
        "accounts/edit_profile.html",
        {"form": form}
    )