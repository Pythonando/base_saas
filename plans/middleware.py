from django.contrib import messages
from django.contrib.messages import constants
from django.shortcuts import redirect
from django.urls import resolve, reverse

_blocked_urls_set = frozenset(
    (
        "dashboard",
        
    )
)
def plan_access_control(get_response):
    def middleware(request):
        if not request.user.is_authenticated:
            return get_response(request)

        try:
            url_name = resolve(request.path).url_name
        except Exception:
            return get_response(request)

        if url_name in _blocked_urls_set:
            if not hasattr(request, "_cached_is_active_plan"):
                request._cached_is_active_plan = request.user.is_active_plan

            if not request._cached_is_active_plan:
                messages.add_message(
                    request,
                    constants.WARNING,
                    "Escolha seu plano para usar a plataforma por 7 dias gratis.",
                )
                return redirect(reverse("accounts:payments_settings"))

        return get_response(request)

    return middleware

