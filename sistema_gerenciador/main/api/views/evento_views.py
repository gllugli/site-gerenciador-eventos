from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.throttling import ScopedRateThrottle

from ...models import Evento, Inscricao
from ..serializers.evento_serializer import EventoSerializer
from main.api.permissions import IsEmailConfirmed
from main.utils.logs import log_evento  # ajuste o caminho se necessário


class EventoListAPIView(generics.ListAPIView):
    """
    Recebe a requisição para mostrar todos os eventos cadastrados
    (com log de consulta via API)
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "consulta_eventos"
    permission_classes = [permissions.IsAuthenticated, IsEmailConfirmed]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Log apenas em sucesso
        if response.status_code == 200:
            # Se sua função log_evento exigir um evento, passe um "evento fake" aqui.
            # Recomendado: atualizar log_evento para aceitar evento=None.
            try:
                log_evento(
                    usuario=getattr(request.user, "perfil", None) or request.user,
                    acao="API_EVENT_LIST",
                    evento=None,
                    detalhes="Consulta de eventos via API.",
                )
            except Exception:
                # não quebra a API por causa de log
                pass

        return response


class EventoDetailAPIView(generics.RetrieveAPIView):
    """
    Recebe uma requisição para mostrar o evento desejado
    (com log de consulta via API)
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailConfirmed]

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if response.status_code == 200:
            try:
                evento = self.get_object()
                log_evento(
                    usuario=getattr(request.user, "perfil", None) or request.user,
                    acao="API_EVENT_DETAIL",
                    evento=evento,
                    detalhes=f"Consulta do evento #{evento.id} via API.",
                )
            except Exception:
                pass

        return response


class EventoInscricaoAPIView(APIView):
    """
    Endpoint para o usuário autenticado se inscrever em um evento específico.
    Reaproveita Evento.pode_inscrever(usuario) para aplicar as regras de negócio.
    (com logs de sucesso e falha)
    """
    permission_classes = [permissions.IsAuthenticated, IsEmailConfirmed]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "inscricao_eventos"

    def post(self, request, pk):
        # 1) Evento
        evento = get_object_or_404(Evento, pk=pk)

        # 2) Usuário (perfil)
        usuario = request.user.perfil

        # 🔎 DEBUG (remova depois se quiser)
        print("TIPO PERFIL:", usuario.tipo_perfil)
        print("STATUS EVENTO:", evento.status)
        print("VAGAS:", evento.quantidade_vagas, "INSCRICOES:", evento.total_inscricoes())
        print("JA INSCRITO:", evento.usuario_ja_inscrito(usuario))

        # 3) Regra de negócio
        pode = evento.pode_inscrever(usuario)

        if not pode:
            try:
                log_evento(
                    usuario=usuario,
                    acao="API_EVENT_SUBSCRIBE_FAIL",
                    evento=evento,
                    detalhes="Tentativa de inscrição via API negada pelas regras do evento.",
                )
            except Exception:
                pass

            return Response(
                {"detail": "Você não pode se inscrever neste evento."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4) Cria a inscrição (evita duplicata)
        inscricao, created = Inscricao.objects.get_or_create(
            evento=evento,
            usuario=usuario,
        )

        if not created:
            return Response(
                {"detail": "Você já está inscrito neste evento."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 5) Log de sucesso
        try:
            log_evento(
                usuario=usuario,
                acao="API_EVENT_SUBSCRIBE",
                evento=evento,
                detalhes=f"Inscrição via API criada. Inscricao #{inscricao.id}.",
            )
        except Exception:
            pass

        # 6) Resposta final
        return Response(
            {
                "detail": "Inscrição realizada com sucesso.",
                "evento_id": evento.id,
                "inscricao_id": inscricao.id,
            },
            status=status.HTTP_201_CREATED,
        )
