from rest_framework import serializers
from ...models import Evento


class EventoSerializer(serializers.ModelSerializer):
    """
    Converte instâncias do modelo evento para JSON
    """

    class Meta:
        model = Evento
        fields = [
            'id',
            'titulo',
            'descricao',
            'status',
            'data_inicio',
            'data_fim',
            'horario_inicio',
            'horario_fim',
            'localizacao',
            'organizador',
        ]
