from django.conf import settings
from django.template import loader
from django.utils.html import strip_tags


def send_mail_sendpulse(subject, email_template_name, context, email_to, name_to=""):
    try:
        from pysendpulse.pysendpulse import PySendPulse
    except ImportError as exc:
        raise RuntimeError(
            "Biblioteca pysendpulse nao instalada. Instale com: pip install pysendpulse"
        ) from exc

    if not settings.CLIENT_ID_SENDPULSE or not settings.CLIENT_SECRET_SENDPULSE:
        raise RuntimeError("Defina CLIENT_ID_SENDPULSE e CLIENT_SECRET_SENDPULSE no ambiente.")

    sp_api_proxy = PySendPulse(settings.CLIENT_ID_SENDPULSE, settings.CLIENT_SECRET_SENDPULSE)

    html_content = loader.render_to_string(email_template_name, context)
    text_content = strip_tags(html_content)

    email = {
        "subject": subject,
        "html": html_content,
        "text": text_content,
        "from": {"name": "Pythonando", "email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"name": name_to, "email": email_to}],
    }

    sp_api_proxy.smtp_send_mail(email)

