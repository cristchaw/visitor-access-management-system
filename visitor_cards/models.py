from django.conf import settings
from django.db import models


class VisitorCard(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        BORROWED = "BORROWED", "Borrowed"
        BLOCKED = "BLOCKED", "Blocked"

    card_number = models.CharField(
        max_length=20,
        unique=True,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_number} - {self.status}"

    class Meta:
        ordering = ["card_number"]


class CardTransaction(models.Model):
    class Status(models.TextChoices):
        BORROWED = "BORROWED", "Borrowed"
        RETURNED = "RETURNED", "Returned"
        OVERDUE = "OVERDUE", "Overdue"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="card_transactions",
    )

    card = models.ForeignKey(
        VisitorCard,
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    access_request = models.OneToOneField(
        "access_requests.AccessRequest",
        on_delete=models.PROTECT,
        related_name="card_transaction",
    )

    borrowed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    due_at = models.DateTimeField()

    returned_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.BORROWED,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.student.username} - "
            f"{self.card.card_number} - {self.status}"
        )

    class Meta:
        ordering = ["-created_at"]

    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_card_transactions",
    )

    issued_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_card_transactions",
    )

    returned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="returned_card_transactions",
    )