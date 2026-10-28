from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from visitor_cards.models import CardTransaction

from .forms import AccessRequestForm
from .models import AccessRequest


def is_security(user):
    return user.is_authenticated and user.role == "SECURITY"


@login_required
def create_access_request(request):
    if request.user.role != "STUDENT":
        return redirect("dashboard")

    # Cek apakah mahasiswa masih memiliki kartu yang belum dikembalikan.
    active_transaction = CardTransaction.objects.filter(
        student=request.user,
        status__in=[
            CardTransaction.Status.BORROWED,
            CardTransaction.Status.OVERDUE,
        ],
    ).exists()

    if active_transaction:
        messages.error(
            request,
            "Kamu masih memiliki kartu yang belum dikembalikan. "
            "Kembalikan kartu sebelumnya sebelum mengajukan akses baru.",
        )
        return redirect("student_access_requests")

    if request.method == "POST":
        form = AccessRequestForm(request.POST)

        if form.is_valid():
            access_request = form.save(commit=False)
            access_request.student = request.user
            access_request.save()

            messages.success(
                request,
                "Permintaan akses berhasil dikirim dan "
                "menunggu persetujuan Security.",
            )
            return redirect("student_access_requests")
    else:
        form = AccessRequestForm()

    return render(
        request,
        "access_requests/create.html",
        {"form": form},
    )


@login_required
def student_access_requests(request):
    if request.user.role != "STUDENT":
        return redirect("dashboard")

    requests = AccessRequest.objects.filter(
        student=request.user
    )

    return render(
        request,
        "access_requests/list.html",
        {"requests": requests},
    )


@user_passes_test(is_security, login_url="/accounts/login/")
def security_requests(request):
    requests = AccessRequest.objects.select_related(
        "student",
        "reviewed_by",
    ).order_by("-created_at")

    return render(
        request,
        "access_requests/security_list.html",
        {"requests": requests},
    )


@require_POST
@user_passes_test(is_security, login_url="/accounts/login/")
def review_request(request, request_id):
    access_request = get_object_or_404(
        AccessRequest,
        id=request_id,
    )

    action = request.POST.get("action")

    if access_request.status != AccessRequest.Status.PENDING:
        messages.error(
            request,
            "Permintaan ini sudah diproses sebelumnya.",
        )
        return redirect("security_requests")

    if action == "approve":
        access_request.status = AccessRequest.Status.APPROVED
        message = "Permintaan berhasil disetujui."

    elif action == "reject":
        access_request.status = AccessRequest.Status.REJECTED
        message = "Permintaan berhasil ditolak."

    else:
        messages.error(request, "Aksi tidak valid.")
        return redirect("security_requests")

    access_request.reviewed_at = timezone.now()
    access_request.reviewed_by = request.user

    access_request.save(
        update_fields=[
            "status",
            "reviewed_at",
            "reviewed_by",
        ]
    )

    messages.success(request, message)
    return redirect("security_requests")