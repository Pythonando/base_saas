from django.contrib import admin

from .models import Plan, UserPlan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "price_monthly", "active")
    search_fields = ("code", "name")


@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "subscription_id", "updated_at")
    list_filter = ("status", "plan")
    search_fields = ("user__email", "subscription_id")

