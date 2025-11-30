from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

telefone_validator = RegexValidator(
    regex=r'^\(\d{2}\)\s\d{5}-\d{4}$',
    message="Formato inválido. Use (XX) XXXXX-XXXX."
)

# Create your models here.


class Usuario(models.Model):

    TIPO_PERFIL_CHOICES = [
        ('AL', 'Aluno'),
        ('PR', 'Professor'),
        ('ADM', 'Administrador'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    telefone = models.CharField(
        max_length=15,
        validators=[telefone_validator],
        null=False,
        blank=False,
        unique=True
    )
    instituicao = models.CharField(max_length=100, null=False, blank=False)

    '''
    PEDIR PARA O PEDRO ADICIONAR CAMPO NO HTML PARA ESCOLHA DO TIPO DE PERFIL
    UM CAMPO DE SELEÇÃO MOSTRANDO AS OPÇÕES ALUNO E PROFESSOR
    '''
    tipo_perfil = models.CharField(
        max_length=3,
        choices=TIPO_PERFIL_CHOICES,
        default='AL'
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}" \
            f" - {self.tipo_perfil}" \
            f" - {self.telefone}" \
            f" - {self.instituicao}"


class Evento(models.Model):

    STATUS_EVENTO = [
        ('Rascunho', 'Rascunho'),
        ('Ativo', 'Ativo'),
        ('Encerrado', 'Encerrado'),
        ('Cancelado', 'Cancelado'),
    ]

    titulo = models.CharField(max_length=100)
    descricao = models.TextField(max_length=1000)
    status = models.CharField(
        max_length=10,
        choices=STATUS_EVENTO,
        default='Rascunho'
    )
    data_inicio = models.DateField(null=False)
    data_fim = models.DateField(null=False)
    horario_inicio = models.TimeField(null=False)
    horario_fim = models.TimeField(null=False)
    localizacao = models.CharField(max_length=200)
    organizador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )


    def clean(self):
        """
        Valida a data inicial, para que não seja antes da data atual 

        Valida a data final, para que seja depois da data inicial 
        """
        if self.data_inicio < timezone.now().date():
            raise ValidationError("A data de início não pode ser anterior à data atual.")
        if self.data_fim < self.data_inicio:
            raise ValidationError("A data final não pode ser menor que a inicial.")


    def __str__(self):
        return self.titulo


class Inscricao(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )
    data_inscricao = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["evento", "usuario"],
                name="unique_inscricao_evento_usuario",
            )
        ]

    def __str__(self):
        return f"Inscrição de {self.usuario} para {self.evento} -" \
            f"{self.data_inscricao}"


class Certificado(models.Model):
    codigo_certificado = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False
    )
    data_emissao = models.DateField(auto_now_add=True)
    inscricao = models.OneToOneField(
        Inscricao,
        on_delete=models.CASCADE,
        related_name="certificado",
    )

    def __str__(self):
        return f"Código Certificado: {self.codigo_certificado}" \
            f"| Data Emissão: {self.data_emissao}" \
            f"| Usuário: {self.inscricao.usuario}" \
            f"| Evento: {self.inscricao.evento}"


class Log(models.Model):
    ...
