from django import forms
from main.models import Inscricao


class InscricaoUpdateForm(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ['evento']
        widgets = {
            'evento': forms.Select(attrs={'class': 'input-field'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        evento = cleaned_data.get('evento')
        usuario = self.instance.usuario  # não estamos editando o usuário

        if evento and usuario:
            conflito = (
                Inscricao.objects
                .filter(evento=evento, usuario=usuario)
                .exclude(pk=self.instance.pk)
                .exists()
            )
            if conflito:
                raise forms.ValidationError(
                    "Já existe uma inscrição deste usuário para este evento."
                )

        return cleaned_data
