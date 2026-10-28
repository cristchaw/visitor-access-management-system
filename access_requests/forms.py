from django import forms
from django.utils import timezone

from .models import AccessRequest


class AccessRequestForm(forms.ModelForm):
    class Meta:
        model = AccessRequest
        fields = ["visit_date", "purpose"]

        labels = {
            "visit_date": "Tanggal Kunjungan",
            "purpose": "Tujuan Kunjungan",
        }

        widgets = {
            "visit_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "purpose": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Jelaskan tujuan kunjunganmu ke Menara Batavia",
                }
            ),
        }

    def clean_visit_date(self):
        visit_date = self.cleaned_data["visit_date"]

        if visit_date < timezone.localdate():
            raise forms.ValidationError(
                "Tanggal kunjungan tidak boleh di masa lalu."
            )

        return visit_date