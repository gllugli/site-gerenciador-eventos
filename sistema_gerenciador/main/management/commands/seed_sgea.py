# main/management/commands/seed_sgea.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from datetime import timedelta, time
import random

from main.models import Usuario, Evento, Inscricao, Certificado, Log


class Command(BaseCommand):
    help = "Derruba e recria dados iniciais (seeding) do SGEA com boa variação."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        random.seed(42)

        # ---------------------------------------------------------------------
        # 1) LIMPA TUDO (ordem segura por FK)
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.WARNING("Limpando banco de dados (tudo será apagado)..."))

        Certificado.objects.all().delete()
        Inscricao.objects.all().delete()
        Evento.objects.all().delete()
        Usuario.objects.all().delete()
        Log.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Banco limpo com sucesso."))

        # ---------------------------------------------------------------------
        # Helpers
        # ---------------------------------------------------------------------
        def gen_password(prefix: str) -> str:
            return f"{prefix}@{random.randint(100,999)}!"

        def gen_phone(seq: int) -> str:
            # Formato: (XX) XXXXX-XXXX
            first = f"9{(1000 + seq) % 10000:04d}"
            last = f"{(2000 + seq) % 10000:04d}"
            return f"(61) {first}-{last}"

        def slugish(n: int) -> str:
            return f"{n:03d}"

        def rand_name() -> str:
            first = random.choice([
                "Ana", "Bruno", "Carla", "Diego", "Eduarda", "Felipe", "Gabriela",
                "Henrique", "Isabela", "João", "Karen", "Lucas", "Marina", "Nicolas",
                "Otávio", "Paula", "Rafael", "Sofia", "Thiago", "Vitória",
            ])
            last = random.choice([
                "Silva", "Souza", "Oliveira", "Santos", "Lima", "Ferreira", "Pereira",
                "Almeida", "Gomes", "Ribeiro", "Carvalho", "Araújo", "Rocha", "Barbosa",
            ])
            return f"{first} {last}"

        def rand_instituicao() -> str:
            return random.choice(["UniCEUB", "UnB", "IFB", "UCB", "IESB"])

        def split_name(full: str):
            parts = full.split()
            if len(parts) == 1:
                return parts[0], ""
            return parts[0], " ".join(parts[1:])

        def make_user(*, email: str, full_name: str, password: str,
                      is_staff: bool = False, is_superuser: bool = False):
            """
            IMPORTANTE:
            - Mantém username = email para compatibilidade com login padrão do seu projeto.
            - NOME DO USUÁRIO fica em first_name/last_name e no perfil Usuario.nome_completo.
            """
            fn, ln = split_name(full_name)
            user = User.objects.create(
                username=email,           # ✅ compatível: login usando email como username
                email=email,
                first_name=fn,
                last_name=ln,
                is_staff=is_staff,
                is_superuser=is_superuser,
            )
            user.set_password(password)
            user.save()
            return user

        def make_perfil(user, *, nome: str, tipo: str, telefone: str,
                        instituicao: str = "", email_confirmado: bool = True) -> Usuario:
            return Usuario.objects.create(
                user=user,
                nome_completo=nome,
                tipo_perfil=tipo,
                telefone=telefone,
                instituicao=instituicao,
                email_confirmado=email_confirmado,
            )

        def make_log(user, acao: str, objeto_tipo: str = "", objeto_id: str = "",
                     descricao: str = "", extras=None):
            Log.objects.create(
                usuario=user,
                acao=acao,
                objeto_tipo=objeto_tipo,
                objeto_id=objeto_id,
                descricao=descricao,
                extras=extras,
            )

        # ---------------------------------------------------------------------
        # 2) USUÁRIOS FIXOS (para você logar e testar)
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.WARNING("Criando usuários fixos de login..."))

        admin_email = "admin@sgea.com"
        admin_pass = "Admin@123"
        admin_nome = "Administrador Geral"
        admin_user = make_user(
            email=admin_email,
            full_name=admin_nome,
            password=admin_pass,
            is_staff=True,
            is_superuser=True,
        )
        admin_perfil = make_perfil(
            admin_user,
            nome=admin_nome,
            tipo="ADM",
            telefone=gen_phone(1),
            instituicao="",
            email_confirmado=True,
        )
        make_log(admin_user, "USER_CREATE", "Usuario", str(admin_perfil.pk), "Seed: criação do admin fixo")

        prof_email = "professor@sgea.com"
        prof_pass = "Professor@123"
        prof_nome = "Professor Carlos Almeida"
        professor_user = make_user(
            email=prof_email,
            full_name=prof_nome,
            password=prof_pass,
            is_staff=False,
            is_superuser=False,
        )
        professor_perfil = make_perfil(
            professor_user,
            nome=prof_nome,
            tipo="PR",
            telefone=gen_phone(2),
            instituicao="UniCEUB",
            email_confirmado=True,
        )
        make_log(admin_user, "USER_CREATE", "Usuario", str(professor_perfil.pk), "Seed: criação do professor fixo")

        aluno_email = "aluno@sgea.com"
        aluno_pass = "Aluno@123"
        aluno_nome = "Aluno João Silva"
        aluno_user = make_user(
            email=aluno_email,
            full_name=aluno_nome,
            password=aluno_pass,
            is_staff=False,
            is_superuser=False,
        )
        aluno_perfil = make_perfil(
            aluno_user,
            nome=aluno_nome,
            tipo="AL",
            telefone=gen_phone(3),
            instituicao="UniCEUB",
            email_confirmado=True,
        )
        make_log(admin_user, "USER_CREATE", "Usuario", str(aluno_perfil.pk), "Seed: criação do aluno fixo")

        # ---------------------------------------------------------------------
        # 3) MAIS USUÁRIOS (>=10 por tipo)
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.WARNING("Criando usuários adicionais (AL/PR/ADM)..."))

        alunos = [aluno_perfil]
        professores = [professor_perfil]
        admins = [admin_perfil]

        target_each = 10
        seq_phone = 10

        # ADM
        while len(admins) < target_each:
            idx = len(admins) + 1
            email = f"organizador{slugish(idx)}@sgea.com"
            nome = f"Organizador {idx} {random.choice(['Silva', 'Souza', 'Pereira', 'Gomes'])}"

            u = make_user(
                email=email,
                full_name=nome,
                password=gen_password("Admin"),
                is_staff=True,
                is_superuser=False,
            )
            perfil = make_perfil(
                u,
                nome=nome,
                tipo="ADM",
                telefone=gen_phone(seq_phone),
                instituicao="",
                email_confirmado=random.choice([True, True, True, False]),
            )
            admins.append(perfil)
            make_log(admin_user, "USER_CREATE", "Usuario", str(perfil.pk), f"Seed: criação {email}")
            seq_phone += 1

        # PR
        while len(professores) < target_each:
            idx = len(professores) + 1
            email = f"prof{slugish(idx)}@sgea.com"
            nome = f"{rand_name()} (Prof {idx})"

            u = make_user(
                email=email,
                full_name=nome.replace(f"(Prof {idx})", "").strip(),
                password=gen_password("Professor"),
            )
            perfil = make_perfil(
                u,
                nome=nome,
                tipo="PR",
                telefone=gen_phone(seq_phone),
                instituicao=rand_instituicao(),
                email_confirmado=random.choice([True, True, False]),
            )
            professores.append(perfil)
            make_log(admin_user, "USER_CREATE", "Usuario", str(perfil.pk), f"Seed: criação {email}")
            seq_phone += 1

        # AL
        while len(alunos) < target_each:
            idx = len(alunos) + 1
            email = f"aluno{slugish(idx)}@sgea.com"
            nome = f"{rand_name()} (Aluno {idx})"

            u = make_user(
                email=email,
                full_name=nome.replace(f"(Aluno {idx})", "").strip(),
                password=gen_password("Aluno"),
            )
            perfil = make_perfil(
                u,
                nome=nome,
                tipo="AL",
                telefone=gen_phone(seq_phone),
                instituicao=rand_instituicao(),
                email_confirmado=random.choice([True, True, True, False]),
            )
            alunos.append(perfil)
            make_log(admin_user, "USER_CREATE", "Usuario", str(perfil.pk), f"Seed: criação {email}")
            seq_phone += 1

        # ---------------------------------------------------------------------
        # 4) EVENTOS (AGORA: MAIS EVENTOS + MAIS "Ativo")
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.WARNING("Criando eventos..."))

        status_choices = [s[0] for s in Evento.STATUS_EVENTO]

        # ✅ Somente UniCEUB - Bloco 1..12 (formato exigido)
        locais = [f"UniCEUB - Bloco {i}" for i in range(1, 13)]

        temas = [
            "Segurança Cibernética", "IA e Mercado", "Python", "GoLang", "Django", "DevOps",
            "Dados e BI", "Carreiras em TI", "LGPD", "Cloud", "Product Management", "Git e Versionamento"
        ]

        # ✅ mais eventos
        total_eventos = 20

        # ✅ aumenta a chance de vir "Ativo" sem mexer na lógica geral (apenas distribuição)
        # (mantém compatível com o que existir em STATUS_EVENTO; se não tiver "Ativo", cai no random normal)
        status_pool = (
            ["Ativo"] * 8 + [s for s in status_choices if s != "Ativo"]
            if "Ativo" in status_choices
            else status_choices
        )

        eventos = []
        base_date = timezone.now().date() + timedelta(days=3)

        for i in range(1, total_eventos + 1):
            tema = random.choice(temas)
            titulo = f"{random.choice(['Palestra', 'Minicurso', 'Mesa redonda', 'Workshop'])}: {tema} #{i}"

            start_day = base_date + timedelta(days=i)
            duration_days = random.choice([0, 0, 1, 2])
            end_day = start_day + timedelta(days=duration_days)

            start_hour = random.choice([8, 9, 10, 14, 16, 18, 19])
            start_minute = random.choice([0, 0, 30])
            hours_len = random.choice([1, 2, 3])
            end_hour = min(start_hour + hours_len, 23)

            horario_inicio = time(start_hour, start_minute)
            horario_fim = time(end_hour, start_minute)

            status = random.choice(status_pool)
            vagas = random.choice([20, 30, 40, 50, 60, 80, 100])

            organizador = random.choice(professores)

            ev = Evento.objects.create(
                titulo=titulo,
                descricao=f"Evento sobre {tema}. Conteúdo com exemplos práticos e espaço para dúvidas.",
                status=status,
                quantidade_vagas=vagas,
                data_inicio=start_day,
                data_fim=end_day,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                localizacao=random.choice(locais),
                organizador=organizador,
            )
            eventos.append(ev)

            make_log(
                admin_user,
                "EVENT_CREATE",
                "Evento",
                str(ev.pk),
                f"Seed: criação do evento '{ev.titulo}'",
                extras={"status": ev.status, "vagas": ev.quantidade_vagas},
            )

        # ---------------------------------------------------------------------
        # 5) INSCRIÇÕES (>=10) + variação de presença
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.WARNING("Criando inscrições..."))

        perfis_inscriveis = alunos + professores
        inscricoes = []
        target_inscricoes = 40

        used_pairs = set()
        attempts = 0
        max_attempts = 2000

        eventos_ativos = [e for e in eventos if e.status == "Ativo"]
        pool_eventos = eventos_ativos if eventos_ativos else eventos

        while len(inscricoes) < target_inscricoes and attempts < max_attempts:
            attempts += 1
            ev = random.choice(pool_eventos)
            us = random.choice(perfis_inscriveis)

            key = (ev.pk, us.pk)
            if key in used_pairs:
                continue

            if Inscricao.objects.filter(evento=ev).count() >= ev.quantidade_vagas:
                continue

            ins = Inscricao.objects.create(
                evento=ev,
                usuario=us,
                presenca_confirmada=random.choice([True, False, False]),
            )
            used_pairs.add(key)
            inscricoes.append(ins)

            make_log(
                us.user,
                "EVENT_SUBSCRIBE",
                "Evento",
                str(ev.pk),
                f"Seed: inscrição de '{us.nome_completo}' no evento '{ev.titulo}'",
                extras={"presenca_confirmada": ins.presenca_confirmada},
            )

        if len(inscricoes) < 10:
            raise RuntimeError("Falha ao gerar pelo menos 10 inscrições. Ajuste os parâmetros do seed.")

        # ---------------------------------------------------------------------
        # 6) CERTIFICADOS (>=10)
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.WARNING("Criando certificados..."))

        confirmadas = [i for i in inscricoes if i.presenca_confirmada]
        base_for_cert = confirmadas if len(confirmadas) >= 10 else inscricoes

        random.shuffle(base_for_cert)
        target_certs = 10

        created_certs = 0
        for ins in base_for_cert:
            if created_certs >= target_certs:
                break
            if hasattr(ins, "certificado"):
                continue

            cert = Certificado.objects.create(inscricao=ins)
            created_certs += 1

            make_log(
                admin_user,
                "CERT_GENERATE",
                "Certificado",
                str(cert.codigo_certificado),
                f"Seed: certificado gerado para '{ins.usuario.nome_completo}'",
                extras={"inscricao_id": ins.pk, "evento_id": ins.evento.pk, "usuario_id": ins.usuario.pk},
            )

        if created_certs < 10:
            raise RuntimeError("Falha ao gerar pelo menos 10 certificados. Ajuste os parâmetros do seed.")

        # ---------------------------------------------------------------------
        # 7) LOGS EXTRAS
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.WARNING("Gerando logs adicionais..."))

        extra_actions = ["EVENT_UPDATE", "EVENT_DELETE", "EVENT_API_QUERY", "CERT_VIEW"]
        for i in range(15):
            acao = random.choice(extra_actions)
            u = random.choice([admin_user, professor_user, aluno_user])
            ev = random.choice(eventos)

            if acao in ["EVENT_UPDATE", "EVENT_DELETE", "EVENT_API_QUERY"]:
                objeto_tipo = "Evento"
                objeto_id = str(ev.pk)
            else:
                objeto_tipo = "Certificado"
                objeto_id = ""

            make_log(
                u,
                acao,
                objeto_tipo,
                objeto_id,
                f"Seed: log extra ({acao})",
                extras={"seed_extra": True, "idx": i},
            )

        # ---------------------------------------------------------------------
        # Resumo + acessos
        # ---------------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS("Seed concluído com sucesso!"))
        self.stdout.write(f"- Users (auth): {User.objects.count()}")
        self.stdout.write(f"- Usuarios (perfil): {Usuario.objects.count()}")
        self.stdout.write(f"- Eventos: {Evento.objects.count()}")
        self.stdout.write(f"- Inscricoes: {Inscricao.objects.count()}")
        self.stdout.write(f"- Certificados: {Certificado.objects.count()}")
        self.stdout.write(f"- Logs: {Log.objects.count()}")

        self.stdout.write(self.style.WARNING("Acessos fixos para teste:"))
        self.stdout.write(f"- ADM: {admin_email} / {admin_pass}")
        self.stdout.write(f"- PR:  {prof_email} / {prof_pass}")
        self.stdout.write(f"- AL:  {aluno_email} / {aluno_pass}")
