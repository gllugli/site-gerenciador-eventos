from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User

from .decorators import admin_required
from .models import Evento, Log, Usuario
from .forms.forms_evento import EventoForm
from .utils.logs import log_evento

@admin_required
def admin_dashboard(request):
    """
    Dashboard administrativo.
    Mostra os logs do sistema com filtros por dia e por usuário.
    """
    # --- filtros (GET) ---
    data_str = request.GET.get("data")           # esperado: YYYY-MM-DD
    usuario_str = request.GET.get("usuario")     # esperado: id (string)

    data = parse_date(data_str) if data_str else None  # date ou None

    logs_qs = (
        Log.objects
        .select_related("usuario")
        .order_by("-data_hora")
    )

    if data:
        logs_qs = logs_qs.filter(data_hora__date=data)

    if usuario_str:
        try:
            usuario_id = int(usuario_str)
            logs_qs = logs_qs.filter(usuario_id=usuario_id)
        except (TypeError, ValueError):
            pass

    # últimos 50 logs após filtros
    logs = logs_qs[:50]

    # ---------------------------------------------------------------------
    # ✅ CORREÇÃO DO ERRO:
    # Você estava fazendo: Usuario.objects.filter(log__isnull=False)
    # mas NÃO existe relação "log" dentro de Usuario.
    #
    # Aqui montamos o dropdown a partir dos IDs que EXISTEM em Log,
    # e buscamos os perfis Usuario corretamente, independente de o FK
    # Log.usuario apontar para auth.User ou para main.Usuario.
    # ---------------------------------------------------------------------
    log_usuario_model = Log._meta.get_field("usuario").remote_field.model

    ids_em_log = (
        Log.objects
        .values_list("usuario_id", flat=True)
        .distinct()
    )

    if log_usuario_model is Usuario:
        # Log.usuario -> main.Usuario
        usuarios_com_log = (
            Usuario.objects
            .filter(id__in=ids_em_log)
            .distinct()
            .order_by("nome_completo")
        )
    elif log_usuario_model is User:
        # Log.usuario -> auth.User, e Usuario tem OneToOne/ForeignKey "user"
        usuarios_com_log = (
            Usuario.objects
            .filter(user_id__in=ids_em_log)
            .distinct()
            .order_by("nome_completo")
        )
    else:
        # fallback seguro (não deve acontecer)
        usuarios_com_log = Usuario.objects.none()

    return render(
        request,
        "main/admin/admin_dashboard.html",
        {
            "logs": logs,
            "usuarios_com_log": usuarios_com_log,
            "filtro_data": data_str or "",
            "filtro_usuario": usuario_str or "",
        },
    )



@admin_required
def admin_event_list(request):
    """
    Lista de eventos + formulário (em modal) para criação rápida.
    """
    eventos = Evento.objects.all().order_by("-data_inicio")
    form_create = EventoForm()  # form vazio para o modal

    return render(
        request,
        "main/admin/admin_events_list.html",
        {
            "eventos": eventos,
            "form_create": form_create,
        },
    )


@admin_required
def admin_event_detail(request, pk):
    """
    Detalhe de um evento específico + formulário de edição.
    """
    evento = get_object_or_404(Evento, pk=pk)
    form = EventoForm(instance=evento)

    return render(
        request,
        "main/admin/admin_event_detail.html",
        {
            "evento": evento,
            "form": form,
        },
    )


@admin_required
def event_create(request):
    """
    Criação de evento a partir do modal na listagem administrativa.
    """
    if request.method != "POST":
        return redirect("admin_event_list")

    form = EventoForm(request.POST, request.FILES)

    if form.is_valid():
        evento = form.save(commit=False)

        # organizador obrigatório (perfil do usuário logado)
        if hasattr(request.user, "perfil"):
            evento.organizador = request.user.perfil

        # dispara as validações de clean() do model
        evento.full_clean()
        evento.save()

        # LOG: criação de evento
        log_evento(
            usuario=request.user,
            acao="EVENT_CREATE",
            evento=evento,
            detalhes="Evento criado via painel admin.",
        )

        return redirect("admin_event_list")

    # se o form tiver erros, recarrega a lista com o form preenchido
    eventos = Evento.objects.all().order_by("-data_inicio")
    return render(
        request,
        "main/admin/admin_events_list.html",
        {
            "eventos": eventos,
            "form_create": form,
        },
    )


@admin_required
def event_update(request, pk):
    """
    Edição de evento a partir da tela de detalhes.
    """
    evento = get_object_or_404(Evento, pk=pk)

    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            evento = form.save()

            # LOG: edição de evento
            log_evento(
                usuario=request.user,
                acao="EVENT_UPDATE",
                evento=evento,
                detalhes="Evento editado via painel admin.",
            )

            return redirect("admin_event_detail", pk=evento.pk)
    else:
        form = EventoForm(instance=evento)

    return render(
        request,
        "main/admin/admin_event_detail.html",
        {
            "evento": evento,
            "form": form,
        },
    )


@admin_required
def event_delete(request, pk):
    """
    Exclusão de evento (confirmada via POST).
    """
    evento = get_object_or_404(Evento, pk=pk)

    if request.method == "POST":
        # guarda informações antes de deletar
        titulo = evento.titulo
        pk_evento = evento.pk

        # LOG: exclusão de evento
        log_evento(
            usuario=request.user,
            acao="EVENT_DELETE",
            evento=evento,
            detalhes=f"Evento '{titulo}' (ID {pk_evento}) deletado via painel admin.",
        )

        evento.delete()
        return redirect("admin_event_list")

    return redirect("admin_event_detail", pk=pk)
