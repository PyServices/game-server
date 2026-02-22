from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view),
    path("signup/", views.signup_view),
    path("logout/", views.logout_view),
    path("me/", views.me),
    path("update/", views.update_profile),
    path("update/password/", views.update_password),
    path("update/otp/", views.update_otp),
    path("update/device-id/", views.update_device_id),
]
