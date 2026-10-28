
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import BlockedUserAuthenticationForm

urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=BlockedUserAuthenticationForm,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "admin/students/",
        views.student_management,
        name="student_management",
    ),
    path(
        "admin/students/<int:user_id>/toggle-block/",
        views.toggle_student_block,
        name="toggle_student_block",
    ),
    path(
        "admin/security/",
        views.security_management,
        name="security_management",
    ),
    path(
        "admin/security/create/",
        views.create_security,
        name="create_security",
    ),
    path(
        "admin/security/<int:user_id>/toggle-block/",
        views.toggle_security_block,
        name="toggle_security_block",
    ),
    path(
        "admin/students/<int:user_id>/delete/",
        views.delete_student,
        name="delete_student",
    ),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    ]
