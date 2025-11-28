from django.contrib import admin
from .models import Usuario, Evento, Inscricao, Certificado

# Register your models here.


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_perfil', 'telefone', 'instituicao')
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'telefone',
        'instituicao'
    )
    list_filter = ('tipo_perfil',)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'status',
        'data_inicio',
        'data_fim',
        'organizador'
    )
    search_fields = (
        'titulo',
        'descricao',
        'localizacao',
        'organizador__user__username',
        'organizador__user__first_name',
        'organizador__user__last_name'
    )
    list_filter = ('status', 'data_inicio', 'data_fim')


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'usuario', 'data_inscricao')
    search_fields = (
        'evento__titulo',
        'usuario__user__username',
        'usuario__user__first_name',
        'usuario__user__last_name'
    )
    list_filter = ('data_inscricao',)


@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'codigo_certificado', 'data_emissao')
    search_fields = (
        'inscricao__evento__titulo',
        'inscricao__usuario__user__username',
        'inscricao__usuario__user__first_name',
        'inscricao__usuario__user__last_name',
        'codigo_certificado'
    )
    list_filter = ('data_emissao',)
