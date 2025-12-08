from django import forms
from ..models import Evento


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            "titulo",
            "descricao",
            "status",
            "quantidade_vagas",
            "data_inicio",
            "data_fim",
            "horario_inicio",
            "horario_fim",
            "localizacao",
            "banner",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # exemplo: aplicar a mesma classe CSS que você já usa
        for field in self.fields.values():
            field.widget.attrs["class"] = "input-field"
