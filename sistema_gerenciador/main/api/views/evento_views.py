from rest_framework import generics, permissions

from ...models import Evento
from ..serializers.evento_serializer import EventoSerializer


class EventoListAPIView(generics.ListAPIView):
    """
    Recebe a requisição para mostrar todos os eventos cadastrados
    """

    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventoDetailAPIView(generics.RetrieveAPIView):
    """
    Recebe uma requisição para mostrar o evento desejado
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]
