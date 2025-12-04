from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ..models import Usuario


class RegistroCompletoForm(UserCreationForm):
    nome_completo = forms.CharField(max_length=50, required=True)
    telefone = forms.CharField(max_length=15, required=True)
    tipo_perfil = forms.ChoiceField(
        choices=[
            ('AL', 'Aluno'),
            ('PR', 'Professor'),
        ]
    )
    instituicao = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'email',
            'telefone',
            'instituicao',
            'tipo_perfil',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # remover help_text da senha (as bolinhas de texto)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

        # adicionar mesma classe em todos os campos
        for field in self.fields.values():
            field.widget.attrs['class'] = 'input-field'

    def save(self, commit=True):
        # 1) Cria o User "base" sem salvar no banco ainda
        user = super().save(commit=False)

        user.first_name = self.cleaned_data['nome_completo']
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']

        # 3) Salva o User se commit=True
        if commit:
            user.save()
            
            Usuario.objects.create(
                user=user,
                nome_completo=self.cleaned_data['nome_completo'],
                telefone=self.cleaned_data['telefone'],
                instituicao=self.cleaned_data['instituicao'],
                tipo_perfil=self.cleaned_data['tipo_perfil'],
                email_confirmado=False
            )


        # 5) Retorna o user (com o perfil já criado)
        return user
