from django.contrib import admin

from .models import VisitorCard, CardTransaction


@admin.register(VisitorCard)
class VisitorCardAdmin(admin.ModelAdmin):
    list_display = ("card_number", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("card_number",)


@admin.register(CardTransaction)
class CardTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "card",
        "access_request",
        "borrowed_at",
        "due_at",
        "returned_at",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "student__username",
        "card__card_number",
    )