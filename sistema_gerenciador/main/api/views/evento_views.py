from rest_framework import generics, permissions

from ...models import Evento
from ..serializers.evento_serializer import EventoSerializer


class EventoListAPIView(generics.ListAPIView):
    queryset = Evento.objects.all()  # Acessa todos os objetos do modelo Evento
    serializer_class = EventoSerializer  # Escolhe qual serializer deve usar para isso
    permission_classes = [permissions.IsAuthenticated]  # Garante que a pessoa esteja autenticada para realizar a ação


class EventoDetailAPIView(generics.RetrieveAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]
