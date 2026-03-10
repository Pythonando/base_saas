import json
import logging
from secrets import token_urlsafe

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from accounts.models import User
from accounts.services import send_mail_sendpulse

from .models import Plan, UserPlan

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class ZoutiWebhookView(View):
    # Projeto base com plano unico: qualquer offer valida cai no STANDARD.
    standard_offer_ids = {
        "prod_offer_zl63c...",
    }

    def post(self, request: HttpRequest):
        if settings.ZOUTI_WEBHOOK_SECRET:
            incoming_secret = request.headers.get("X-Zouti-Secret", "")
            if incoming_secret != settings.ZOUTI_WEBHOOK_SECRET:
                return JsonResponse({"detail": "invalid secret"}, status=403)

        try:
            payload = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "invalid payload"}, status=400)

        customer = payload.get("customer", {})
        items = payload.get("items", [])
        product_offer_id = (items[0] if items else {}).get("product_offer_id")
        customer_email = customer.get("email")

        if not customer_email or not product_offer_id:
            return JsonResponse({"detail": "missing customer email or offer id"}, status=400)

        if product_offer_id not in self.standard_offer_ids:
            return HttpResponse(status=200)

        generated_password = token_urlsafe(6)
        user, created = User.objects.get_or_create(email=customer_email)
        if created:
            user.set_password(generated_password)
            user.save(update_fields=["password"])

        plan = Plan.get_standard_plan()
        status = (
            UserPlan.STATUS_ACTIVE
            if payload.get("status") == "PAID"
            else UserPlan.STATUS_CANCELLED
        )
        UserPlan.objects.update_or_create(
            user=user,
            defaults={
                "plan": plan,
                "status": status,
                "subscription_id": payload.get("id", ""),
            },
        )

        if created and status == UserPlan.STATUS_ACTIVE:
            try:
                print('1')
                send_mail_sendpulse(
                    "Acesso liberado | Plano Standard",
                    "email/subscription_confirmed.html",
                    context={"email": customer_email, "password": generated_password},
                    email_to=customer_email,
                )
            except Exception:
                logger.exception("Falha ao enviar e-mail de boas-vindas via SendPulse.")

        return HttpResponse(status=200)

