from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
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
    quantidade_vagas = models.IntegerField(
        null=False, 
        default=0,
        validators=[MinValueValidator(0)]
        )
    banner = models.ImageField(
        upload_to="banners/",
        null=True,
        blank=True,
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
        Validações:
        - data_inicio não pode ser anterior à data atual
        - data_fim não pode ser menor que data_inicio
        - horario_fim deve ser posterior a horario_inicio
        """
        erros = {}

        # Datas
        if self.data_inicio < timezone.now().date():
            erros["data_inicio"] = "A data de início não pode ser anterior à data atual."

        if self.data_fim < self.data_inicio:
            erros["data_fim"] = "A data final não pode ser menor que a data inicial."

        # Horários
        if self.horario_fim <= self.horario_inicio:
            erros["horario_fim"] = "O horário de término deve ser posterior ao horário de início."

        if self.banner:
            max_size = 2 * 1024 * 1024  # 2 MB em bytes

            if self.banner.size > max_size:
                erros["banner"] = "O banner não pode ultrapassar 2MB."

            # 2) Tipo de arquivo (só imagens)
            content_type = getattr(self.banner.file, "content_type", None)

            if content_type is not None and not content_type.startswith("image/"):
                erros["banner"] = "O arquivo de banner deve ser uma imagem válida."

        if erros:
            raise ValidationError(erros)


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

    @property
    def usuario(self):
        return self.inscricao.usuario

    @property
    def evento(self):
        return self.inscricao.evento

    def __str__(self):
        return f"Certificado de {self.usuario} – {self.evento}"


class Log(models.Model):
    ...
