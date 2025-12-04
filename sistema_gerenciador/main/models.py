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

    nome_completo = models.CharField(max_length=50, default='Usuário')
    telefone = models.CharField(
        max_length=15,
        validators=[telefone_validator],
        null=False,
        blank=False,
        unique=True
    )
    instituicao = models.CharField(max_length=100, null=False, blank=True)
    email_confirmado = models.BooleanField(default=False)  # Feito para guardar se o usuário confirmou o email 

    tipo_perfil = models.CharField(
        max_length=3,
        choices=TIPO_PERFIL_CHOICES,
        default='AL'
    )


    def perfil_aluno(self):
        return self.tipo_perfil == 'AL'


    def perfil_professor(self):
        return self.tipo_perfil == 'PR'


    def perfil_adm(self):
        return self.tipo_perfil == 'ADM'


    def pode_se_inscrever(self):
        return self.tipo_perfil in ['AL', 'PR']


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
    quantidade_vagas = models.IntegerField(null=False, default=0)
    data_inicio = models.DateField(null=False)
    data_fim = models.DateField(null=False)
    horario_inicio = models.TimeField(null=False)
    horario_fim = models.TimeField(null=False)
    localizacao = models.CharField(max_length=200)
    organizador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )


    def total_inscricoes(self):
        return self.inscricao.count()
    

    def tem_vagas(self):
        return self.quantidade_vagas > self.total_inscricoes()


    def usuario_ja_inscrito(self, usuario):
        return self.inscricao.filter(usuario=usuario).exists()
    

    def pode_inscrever(self, usuario):
        # 1) Verifica se o perfil do usuário permite inscrição
        if not usuario.pode_se_inscrever():
            return False

        # 2) Evento precisa estar Ativo
        if self.status != 'Ativo':
            return False

        # 3) Verifica se ainda há vagas
        if not self.tem_vagas():
            return False

        # 4) Verifica se o usuário já está inscrito
        if self.usuario_ja_inscrito(usuario):
            return False

        # Se passou em todas as verificações, pode inscrever
        return True


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
        on_delete=models.CASCADE,
        related_name="inscricao"
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
