from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, time

from main.models import Usuario, Evento, Inscricao


class Command(BaseCommand):
    help = "Cria dados iniciais (seeding) do SGEA."

    def handle(self, *args, **options):
        User = get_user_model()

        # --------------------- SEEDING Usuários --------------------------------

        # 1) Usuário Administrador
        administrador_user, created = User.objects.get_or_create(
            username="admin@sgea.com",
            defaults={
                "email": "admin@sgea.com",
            },
        )

        if created:
            administrador_user.set_password("Admin@123")
            administrador_user.save()
            self.stdout.write("Usuário Administrador criado.")
        else:
            self.stdout.write("Usuário Administrador já existia.")

        # Agora cria (ou garante) o perfil na sua tabela Usuario
        administrador_perfil, created = Usuario.objects.get_or_create(
            user=administrador_user,
            defaults={
                "nome_completo": "administrador1",
                "tipo_perfil": "ADM",  
                "telefone": "(61) 99999-9999",
                "email_confirmado": True
            },
        )

        if created:
            administrador_user.is_staff = True
            administrador_user.is_superuser = True
            administrador_user.set_password("Admin@123")
            administrador_user.save()
            
            self.stdout.write("Perfil ADMINISTRADOR criado.")
        else:
            self.stdout.write("Perfil ADMINISTRADOR já existia.")

        
        # 2) Usuário Professor
        professor_user, created = User.objects.get_or_create(
            username="professor@sgea.com",
            defaults={
                "email": "professor@sgea.com",
            },
        )

        if created:
            professor_user.set_password("Professor@123")
            professor_user.save()
            self.stdout.write("Usuário Professor criado.")
        else:
            self.stdout.write("Usuário Professor já existia.")

        # Agora cria (ou garante) o perfil na sua tabela Usuario
        professor_perfil, created = Usuario.objects.get_or_create(
            user=professor_user,
            defaults={
                "nome_completo": "Professor 1",
                "tipo_perfil": "PR",  
                "telefone": "(61) 99999-8888",
                "instituicao": "UniCEUB",
                "email_confirmado": True
            },
        )

        if created:
            self.stdout.write("Perfil PROFESSOR criado.")
        else:
            self.stdout.write("Perfil PROFESSOR já existia.")


        # 3) Usuário Aluno
        aluno_user, created = User.objects.get_or_create(
            username="aluno@sgea.com",
            defaults={
                "email": "aluno@sgea.com",
            },
        )

        if created:
            aluno_user.set_password("Aluno@123")
            aluno_user.save()
            self.stdout.write("Usuário Aluno criado.")
        else:
            self.stdout.write("Usuário Aluno já existia.")

        # Agora cria (ou garante) o perfil na sua tabela Usuario
        aluno_perfil, created = Usuario.objects.get_or_create(
            user=aluno_user,
            defaults={
                "nome_completo": "Aluno 1",
                "tipo_perfil": "AL",  
                "telefone": "(61) 99999-7777",
                "instituicao": "UniCEUB",
                "email_confirmado": True
            },
        )

        if created:
            self.stdout.write("Perfil ALUNO criado.")
        else:
            self.stdout.write("Perfil ALUNO já existia.")


        # --------------------- SEEDING EVENTOS --------------------------------

        data_base = timezone.now().date()
        data_inicio = data_base + timedelta(days=7)
        data_fim = data_inicio + timedelta(days=1)

        horario_inicio = time(19,0)
        horario_fim = time(21,0)


        evento1, created = Evento.objects.get_or_create(
            titulo = "Palestra Segurança Cibernética",
            defaults={
                "descricao": "Palestra introdutória sobre conceitos básicos de segurança cibernética.",
                "status": "Ativo",
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "horario_inicio": horario_inicio,
                "horario_fim": horario_fim,
                "localizacao": "UniCEUB",
                "organizador": administrador_perfil,
            },
        )

        if created:
            self.stdout.write("Evento criado.")
        else:
            self.stdout.write("Evento já existia.")


        evento2, created = Evento.objects.get_or_create(
            titulo = "Mesa redonda: IA substituirá os Devs no futuro?",
            defaults={
                "descricao": "Discussão sobre a possibilidade da IA tomar o lugar dos Devs futuramente.",
                "status": "Rascunho",
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "horario_inicio": horario_inicio,
                "horario_fim": horario_fim,
                "localizacao": "UniCEUB",
                "organizador": administrador_perfil,
            },
        )

        if created:
            self.stdout.write("Evento criado.")
        else:
            self.stdout.write("Evento já existia.")

        
        evento3, created = Evento.objects.get_or_create(
            titulo = "Minicurso de Python Avançado",
            defaults={
                "descricao": "Minicurso ofertado pela Monitoria de TI.",
                "status": "Cancelado",
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "horario_inicio": horario_inicio,
                "horario_fim": horario_fim,
                "localizacao": "UniCEUB",
                "organizador": administrador_perfil,
            },
        )

        if created:
            self.stdout.write("Evento criado.")
        else:
            self.stdout.write("Evento já existia.")


        # ------------------------- SEDDING INSCRICAO -------------------

        inscricao, created = Inscricao.objects.get_or_create(
            usuario = professor_perfil, 
            evento = evento1
        )

        if created:
            self.stdout.write(f'Inscrição no evento "{evento1.titulo}" realizada.')
        else:
            self.stdout.write(f'Inscrição no evento "{evento1.titulo}" já realizada.')


        inscricao, created = Inscricao.objects.get_or_create(
            usuario = professor_perfil, 
            evento = evento2
        )

        if created:
            self.stdout.write(f'Inscrição no evento "{evento2.titulo}" realizada.')
        else:
            self.stdout.write(f'Inscrição no evento "{evento2.titulo}" já realizada.')

        
        inscricao, created = Inscricao.objects.get_or_create(
            usuario = aluno_perfil, 
            evento = evento3
        )

        if created:
            self.stdout.write(f'Inscrição no evento "{evento3.titulo}" realizada.')
        else:
            self.stdout.write(f'Inscrição no evento "{evento3.titulo}" já realizada.')


        self.stdout.write(self.style.SUCCESS("Seeding concluído."))

