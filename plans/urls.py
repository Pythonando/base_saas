from django.urls import path

from .views import ZoutiWebhookView

app_name = "plans"

urlpatterns = [
    path("zouti/", ZoutiWebhookView.as_view(), name="zouti_webhook"),
]

