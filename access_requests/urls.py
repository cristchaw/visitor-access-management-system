from django.urls import path

from . import views


urlpatterns = [
    path(
        "create/",
        views.create_access_request,
        name="create_access_request",
    ),
    path(
        "my-requests/",
        views.student_access_requests,
        name="student_access_requests",
    ),
    path(
        "security/",
        views.security_requests,
        name="security_requests",
    ),
    path(
        "security/<int:request_id>/review/",
        views.review_request,
        name="review_request",
    ),
]