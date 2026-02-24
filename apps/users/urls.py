from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.search_users),
    path("login/", views.login_view),
    path("login/guest/", views.login_guest),
    path("login/otp/", views.login_otp),
    path("login/otp/verify/", views.login_otp_verify),
    path("login/email-phone/", views.login_email_phone),
    path("login/refresh/", views.token_refresh),
    path("signup/", views.signup_view),
    path("logout/", views.logout_view),
    path("me/", views.me),
    path("update/", views.update_profile),
    path("update/password/", views.update_password),
    path("update/otp/", views.update_otp),
    path("update/device-id/", views.update_device_id),
]
