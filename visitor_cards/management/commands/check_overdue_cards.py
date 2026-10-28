from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from visitor_cards.models import CardTransaction, VisitorCard


class Command(BaseCommand):
    help = "Memblokir kartu dan akun mahasiswa yang terlambat."

    def handle(self, *args, **options):
        now = timezone.now()

        overdue_ids = list(
            CardTransaction.objects.filter(
                status=CardTransaction.Status.BORROWED,
                due_at__lte=now,
            ).values_list("id", flat=True)
        )

        processed = 0

        for transaction_id in overdue_ids:
            with transaction.atomic():
                item = (
                    CardTransaction.objects.select_for_update()
                    .filter(
                        pk=transaction_id,
                        status=CardTransaction.Status.BORROWED,
                        due_at__lte=now,
                    )
                    .first()
                )

                if item is None:
                    continue

                item.status = CardTransaction.Status.OVERDUE
                item.save(update_fields=["status"])

                VisitorCard.objects.filter(
                    pk=item.card_id
                ).update(status=VisitorCard.Status.BLOCKED)

                User.objects.filter(
                    pk=item.student_id
                ).update(
                    is_blocked=True,
                    overdue_blocked=True,
                )

                processed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Pemeriksaan selesai. {processed} transaksi terlambat diproses."
            )
        )