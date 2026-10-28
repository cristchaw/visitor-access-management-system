from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Student Email",
        help_text="Use your @student.president.ac.id email address.",
    )
    student_id = forms.CharField(
        required=True,
        max_length=30,
        label="Student ID (NIM)",
    )
    phone = forms.CharField(
        required=False,
        max_length=20,
        label="Phone Number",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "student_id",
            "phone",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if not email.endswith("@student.president.ac.id"):
            raise forms.ValidationError(
                "Registration requires an @student.president.ac.id email."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.student_id = self.cleaned_data["student_id"].strip()
        user.phone = self.cleaned_data["phone"].strip()
        user.role = User.Role.STUDENT

        if commit:
            user.save()

        return user

from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class BlockedUserAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if user.is_blocked:
            raise ValidationError(
                "Akun Anda sedang diblokir. "
                "Silakan hubungi Admin.",
                code="account_blocked",
            )

class SecurityCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nama Depan",
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Nama Belakang",
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Nomor Telepon",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Email ini sudah digunakan."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.phone = self.cleaned_data["phone"].strip()
        user.role = User.Role.SECURITY
        user.is_blocked = False

        if commit:
            user.save()

        return user

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "student_id",
            "phone",
        ]

        labels = {
            "first_name": "Nama Depan",
            "last_name": "Nama Belakang",
            "email": "Email Mahasiswa",
            "student_id": "NIM",
            "phone": "Nomor Telepon",
        }

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Masukkan nama depan",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Masukkan nama belakang",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "nama@student.president.ac.id",
                }
            ),
            "student_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Masukkan NIM",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Masukkan nomor telepon",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()

        if not email.endswith("@student.president.ac.id"):
            raise forms.ValidationError(
                "Email harus menggunakan domain "
                "@student.president.ac.id."
            )

        return email