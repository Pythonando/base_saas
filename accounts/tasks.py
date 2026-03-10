from .services import send_mail_sendpulse


def task_send_mail_sendpulse(subject, email_template_name, **kwargs):
    context = {
        "email": kwargs["email"],
        "site_name": kwargs["site_name"],
        "domain": kwargs["domain"],
        "uid": kwargs["uid"],
        "token": kwargs["token"],
        "protocol": kwargs["protocol"],
    }
    send_mail_sendpulse(
        subject=subject,
        email_template_name=email_template_name,
        context=context,
        email_to=kwargs["email_to"],
    )

