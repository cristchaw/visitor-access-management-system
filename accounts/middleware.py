from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


class BlockedStudentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if (
            user.is_authenticated
            and getattr(user, "role", None) in ("STUDENT", "SECURITY")
            and getattr(user, "is_blocked", False)
        ):
            logout(request)
            messages.error(
                request,
                "Akun Anda diblokir. Silakan hubungi Admin."
            )
            return redirect("login")

        return self.get_response(request)