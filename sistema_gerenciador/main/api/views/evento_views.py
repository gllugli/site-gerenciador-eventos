from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.throttling import ScopedRateThrottle
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from ...models import Evento, Inscricao
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


class EventoInscricaoAPIView(APIView):
    """
    Endpoint para o usuário autenticado se inscrever em um evento específico.
    Reaproveita Evento.pode_inscrever(usuario) para aplicar as regras de negócio.
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "inscricao_eventos"

    def post(self, request, pk):
        evento = get_object_or_404(Evento, pk=pk)

        # Use o mesmo "usuario" que você já usa nas suas regras de negócio:
        # se o método espera o perfil (Usuario), use request.user.usuario
        usuario = request.user  # ou request.user.usuario, conforme seu modelo

        # Aqui você reaproveita a regra de negócio centralizada no modelo
        # Ajuste se seu pode_inscrever retornar (bool, mensagem) em vez de só bool
        pode = evento.pode_inscrever(usuario)

        if not pode:
            return Response(
                {"detail": "Você não pode se inscrever neste evento."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cria a inscrição (evitando duplicata, por segurança)
        inscricao, created = Inscricao.objects.get_or_create(
            evento=evento,
            usuario=usuario,  # ajuste o campo conforme o model Inscricao
        )

        if not created:
            # Se chegar aqui, significa que já existia inscrição (fallback extra)
            return Response(
                {"detail": "Você já está inscrito neste evento."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "Inscrição realizada com sucesso.",
                "evento_id": evento.id,
                "inscricao_id": inscricao.id,
            },
            status=status.HTTP_201_CREATED,
        )

