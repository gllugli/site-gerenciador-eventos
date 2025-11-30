from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from main.models import Usuario  # ajuste se o nome do app/model for outro


class Command(BaseCommand):
    help = "Cria dados iniciais (seeding) do SGEA."

    def handle(self, *args, **options):
        User = get_user_model()

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
                "tipo_perfil": "ADM",  
                "telefone": "(61) 99999-9999",
                "instituicao": "UniCEUB",
            },
        )

        if created:
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
                "tipo_perfil": "PR",  
                "telefone": "(61) 99999-8888",
                "instituicao": "UniCEUB",
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
                "tipo_perfil": "AL",  
                "telefone": "(61) 99999-7777",
                "instituicao": "UniCEUB",
            },
        )

        if created:
            self.stdout.write("Perfil ALUNO criado.")
        else:
            self.stdout.write("Perfil ALUNO já existia.")


        self.stdout.write(self.style.SUCCESS("Seeding concluído."))
