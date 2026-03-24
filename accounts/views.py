import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.shortcuts import redirect, render
from django.utils import timezone

from plans.models import UserPlan

from .forms import LoginForm, RegisterForm
from .models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Login realizado com sucesso.")
        return redirect("accounts:dashboard")

    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Cadastro realizado com sucesso.")
        return redirect("accounts:dashboard")

    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard_view(request):
    return render(request, "accounts/dashboard.html")


@login_required
def payments_settings_view(request):
    return render(request, "accounts/payments_settings.html")


@login_required
def admin_dashboard_view(request):
    if not request.user.is_staff:
        raise PermissionDenied("Apenas administradores podem acessar esta pagina.")

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    active_subscriptions = UserPlan.objects.filter(status=UserPlan.STATUS_ACTIVE)
    cancelled_subscriptions = UserPlan.objects.filter(status=UserPlan.STATUS_CANCELLED)

    mrr = active_subscriptions.aggregate(
        total=Coalesce(
            Sum("plan__price_monthly"),
            Value(0, output_field=DecimalField(max_digits=10, decimal_places=2)),
        )
    )["total"]
    total_users = User.objects.count()
    users_with_plan = UserPlan.objects.count()
    users_without_plan = max(total_users - users_with_plan, 0)
    active_users = active_subscriptions.count()
    cancelled_users = cancelled_subscriptions.count()
    registered_last_30_days = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).count()
    cancelled_last_30_days = cancelled_subscriptions.filter(
        updated_at__gte=thirty_days_ago
    ).count()

    churn_rate = (cancelled_users / users_with_plan * 100) if users_with_plan else 0
    churn_30_days_rate = (
        cancelled_last_30_days / users_with_plan * 100 if users_with_plan else 0
    )
    conversion_to_plan_rate = (users_with_plan / total_users * 100) if total_users else 0
    active_conversion_rate = (active_users / total_users * 100) if total_users else 0

    plans_breakdown = (
        active_subscriptions.values("plan__name")
        .annotate(
            users=Count("id"),
            mrr=Coalesce(
                Sum("plan__price_monthly"),
                Value(0, output_field=DecimalField(max_digits=10, decimal_places=2)),
            ),
        )
        .order_by("plan__name")
    )
    chart_labels = [item["plan__name"] for item in plans_breakdown]
    chart_users = [item["users"] for item in plans_breakdown]
    chart_mrr = [float(item["mrr"]) for item in plans_breakdown]

    monthly_registrations_queryset = (
        User.objects.annotate(month=TruncMonth("date_joined"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )
    monthly_new_paid_queryset = (
        UserPlan.objects.filter(status=UserPlan.STATUS_ACTIVE)
        .annotate(month=TruncMonth("updated_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )
    monthly_cancellations_queryset = (
        UserPlan.objects.filter(status=UserPlan.STATUS_CANCELLED)
        .annotate(month=TruncMonth("updated_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )
    monthly_registrations_map = {
        item["month"]: item["total"] for item in monthly_registrations_queryset if item["month"]
    }
    monthly_new_paid_map = {
        item["month"]: item["total"] for item in monthly_new_paid_queryset if item["month"]
    }
    monthly_cancellations_map = {
        item["month"]: item["total"] for item in monthly_cancellations_queryset if item["month"]
    }
    timeline_months = sorted(
        set(monthly_registrations_map.keys())
        | set(monthly_new_paid_map.keys())
        | set(monthly_cancellations_map.keys())
    )
    timeline_labels = [month.strftime("%m/%Y") for month in timeline_months]
    timeline_registrations = [
        monthly_registrations_map.get(month, 0) for month in timeline_months
    ]
    timeline_new_paid = [monthly_new_paid_map.get(month, 0) for month in timeline_months]
    timeline_cancellations = [
        monthly_cancellations_map.get(month, 0) for month in timeline_months
    ]

    context = {
        "mrr": mrr,
        "total_users": total_users,
        "users_with_plan": users_with_plan,
        "users_without_plan": users_without_plan,
        "active_users": active_users,
        "cancelled_users": cancelled_users,
        "registered_last_30_days": registered_last_30_days,
        "cancelled_last_30_days": cancelled_last_30_days,
        "churn_rate": churn_rate,
        "churn_30_days_rate": churn_30_days_rate,
        "conversion_to_plan_rate": conversion_to_plan_rate,
        "active_conversion_rate": active_conversion_rate,
        "chart_labels_json": json.dumps(chart_labels),
        "chart_users_json": json.dumps(chart_users),
        "chart_mrr_json": json.dumps(chart_mrr),
        "status_labels_json": json.dumps(["Ativos", "Cancelados", "Sem plano"]),
        "status_values_json": json.dumps(
            [active_users, cancelled_users, users_without_plan]
        ),
        "timeline_labels_json": json.dumps(timeline_labels),
        "timeline_registrations_json": json.dumps(timeline_registrations),
        "timeline_new_paid_json": json.dumps(timeline_new_paid),
        "timeline_cancellations_json": json.dumps(timeline_cancellations),
    }
    return render(request, "accounts/admin_dashboard.html", context)


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Voce saiu da sua conta.")
    return redirect("accounts:login")

