from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ..models import Usuario


class RegistroCompletoForm(UserCreationForm):
    nome_completo = forms.CharField(max_length=50, required=True)
    telefone = forms.CharField(max_length=15, required=True)
    tipo_perfil = forms.ChoiceField(
        choices=[
            ("AL", "Aluno"),
            ("PR", "Professor"),
        ]
    )
    instituicao = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["email", "password1", "password2"]

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()

        if User.objects.filter(username__iexact=email).exists():
            raise ValidationError("Já existe um usuário cadastrado com este e-mail.")

        return email

    def clean_telefone(self):
        telefone = (self.cleaned_data.get("telefone") or "").strip()

        if Usuario.objects.filter(telefone=telefone).exists():
            raise ValidationError("Este telefone já está cadastrado.")

        return telefone

    def save(self, commit=True):
        user = super().save(commit=False)

        email = self.cleaned_data["email"].lower().strip()
        nome = self.cleaned_data["nome_completo"].strip()

        user.username = email
        user.email = email
        user.first_name = nome
        user.is_active = False  # 🔒 só ativa após confirmação

        if commit:
            user.save()

            Usuario.objects.create(
                user=user,
                nome_completo=nome,
                telefone=self.cleaned_data["telefone"].strip(),
                instituicao=self.cleaned_data["instituicao"].strip(),
                tipo_perfil=self.cleaned_data["tipo_perfil"],
                email_confirmado=False,
            )

        return user
