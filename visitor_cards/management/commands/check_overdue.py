from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from visitor_cards.models import CardTransaction, VisitorCard


class Command(BaseCommand):
    help = "Memeriksa kartu terlambat dan memblokir kartu serta akun mahasiswa."

    def handle(self, *args, **options):
        now = timezone.now()

        overdue_ids = list(
            CardTransaction.objects.filter(
                status=CardTransaction.Status.BORROWED,
                due_at__lt=now,
            ).values_list("id", flat=True)
        )

        updated_count = 0

        for transaction_id in overdue_ids:
            with transaction.atomic():
                item = (
                    CardTransaction.objects
                    .select_for_update()
                    .select_related("student", "card")
                    .get(pk=transaction_id)
                )

                # Periksa kembali status dan batas waktu.
                if (
                    item.status != CardTransaction.Status.BORROWED
                    or item.due_at >= now
                ):
                    continue

                # Ubah status transaksi menjadi OVERDUE.
                item.status = CardTransaction.Status.OVERDUE
                item.save(update_fields=["status"])

                # Blokir kartu yang terlambat dikembalikan.
                card = VisitorCard.objects.select_for_update().get(
                    pk=item.card_id
                )
                card.status = VisitorCard.Status.BLOCKED
                card.save(update_fields=["status"])

                # Blokir akun mahasiswa.
                student = User.objects.select_for_update().get(
                    pk=item.student_id
                )
                student.is_blocked = True
                student.overdue_blocked = True
                student.save(
                    update_fields=["is_blocked", "overdue_blocked"]
                )

                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Pemeriksaan selesai. {updated_count} transaksi "
                "berubah menjadi OVERDUE."
            )
        )
