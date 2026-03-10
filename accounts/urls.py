from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from .forms import SendPulsePasswordResetForm
from .views import (
    admin_dashboard_view,
    dashboard_view,
    login_view,
    logout_view,
    payments_settings_view,
    register_view,
)

app_name = "accounts"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("cadastro/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("admin/dashboard/", admin_dashboard_view, name="admin_dashboard"),
    path("planos/", payments_settings_view, name="payments_settings"),
    path("logout/", logout_view, name="logout"),
    path(
        "senha/recuperar/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset_form.html",
            email_template_name="email/reset_password.html",
            form_class=SendPulsePasswordResetForm,
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "senha/recuperar/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "senha/redefinir/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "senha/redefinir/concluido/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

