# main/utils/logs.py

def log_evento(usuario, acao, evento, detalhes=""):
    """
    Registra uma ação relacionada a um evento.
    'acao' deve ser um dos códigos definidos em Log.ACOES
    (ex.: 'EVENT_CREATE', 'EVENT_UPDATE', 'EVENT_DELETE').
    """
    # import dentro da função evita qualquer problema de ordem de import
    from ..models import Log

    log = Log.objects.create(
        usuario=usuario,
        acao=acao,                 # ex.: 'EVENT_CREATE'
        objeto_tipo="Evento",      # nome do tipo de objeto
        objeto_id=str(evento.pk),  # ID do evento
        descricao=detalhes,        # texto descritivo
    )

    # DEBUG opcional: ver no terminal se está criando
    print("LOG CRIADO:", log.pk, log.acao, log.objeto_tipo, log.objeto_id)
