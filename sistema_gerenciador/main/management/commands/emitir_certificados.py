# main/management/commands/emitir_certificados.py

from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from main.models import Evento, Inscricao, Certificado


class Command(BaseCommand):
    help = (
        "Encerra automaticamente eventos cujo fim <= agora (se estiverem Ativo) "
        "e emite certificados para eventos encerrados (exceto Cancelado/Rascunho)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas simula; não altera status nem cria certificados.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        agora = timezone.localtime()

        total_eventos_encerrados = 0
        total_eventos_processados = 0
        total_eventos_pulados = 0

        total_inscricoes = 0
        total_criados = 0
        total_ja_existiam = 0

        # Considera eventos que podem gerar certificados (nunca para Cancelado/Rascunho)
        eventos = Evento.objects.exclude(status__in=["Cancelado", "Rascunho"])

        for evento in eventos:
            fim_naive = datetime.combine(evento.data_fim, evento.horario_fim)
            fim = timezone.make_aware(fim_naive) if timezone.is_naive(fim_naive) else fim_naive

            # Se ainda não terminou, não faz nada
            if fim > agora:
                total_eventos_pulados += 1
                continue

            # Se terminou e ainda está Ativo, encerra automaticamente
            if evento.status == "Ativo":
                if not dry_run:
                    Evento.objects.filter(pk=evento.pk).update(status="Encerrado")
                total_eventos_encerrados += 1
                evento.status = "Encerrado"  # mantém consistência no loop

            # Se não estiver Encerrado aqui, não emite
            if evento.status != "Encerrado":
                continue

            inscricoes = (
                Inscricao.objects
                .filter(evento=evento)
                .select_related("usuario", "evento")
            )

            if not inscricoes.exists():
                continue

            total_eventos_processados += 1

            for insc in inscricoes:
                total_inscricoes += 1

                if dry_run:
                    if hasattr(insc, "certificado"):
                        total_ja_existiam += 1
                    else:
                        total_criados += 1
                    continue

                with transaction.atomic():
                    _, created = Certificado.objects.get_or_create(inscricao=insc)
                    if created:
                        total_criados += 1
                    else:
                        total_ja_existiam += 1

        self.stdout.write(self.style.SUCCESS("Rotina automática finalizada."))
        self.stdout.write(f"Eventos encerrados automaticamente (Ativo -> Encerrado): {total_eventos_encerrados}")
        self.stdout.write(f"Eventos processados para emissão: {total_eventos_processados}")
        self.stdout.write(f"Eventos pulados (ainda não terminou): {total_eventos_pulados}")
        self.stdout.write(f"Inscrições avaliadas: {total_inscricoes}")
        self.stdout.write(f"Certificados criados: {total_criados}")
        self.stdout.write(f"Já existiam: {total_ja_existiam}")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN: nenhuma alteração foi aplicada no banco."))
