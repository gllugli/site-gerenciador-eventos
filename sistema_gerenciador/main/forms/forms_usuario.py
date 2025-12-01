from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ..models import Usuario


class RegistroCompletoForm(UserCreationForm):
    telefone = forms.CharField(max_length=20, required=True)
    tipo_perfil = forms.ChoiceField(
        choices=[
            ('AL', 'Aluno'),
            ('PR', 'Professor'),
        ]
    )
    instituicao = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'first_name',
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
