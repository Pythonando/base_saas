from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm

from .models import User
from .tasks import task_send_mail_sendpulse


class LoginForm(forms.Form):
    email = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user = authenticate(email=email, password=password)
            if not self.user:
                raise forms.ValidationError("E-mail ou senha invalidos.")
        return cleaned_data

    def get_user(self):
        return getattr(self, "user", None)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)


class SendPulsePasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        users = list(self.get_users(email))
        if not users:
            raise forms.ValidationError(
                "Nao encontramos uma conta ativa com esse e-mail."
            )
        return email

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        task_send_mail_sendpulse(
            "Recuperacao de senha | Pythonando",
            "email/reset_password.html",
            email_to=to_email,
            email=context["email"],
            site_name=context["site_name"],
            domain=context["domain"],
            uid=context["uid"],
            token=context["token"],
            protocol=context["protocol"],
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        css_classes = (
            "block w-full rounded-md border border-slate-300 px-3 py-2 "
            "outline-none ring-blue-400 focus:ring"
        )
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": css_classes})

