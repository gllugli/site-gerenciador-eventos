from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash, password_validation
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.core import signing
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError  # se quiser capturar erro genérico do token
from django.http import HttpResponseForbidden
from django.http import Http404

from django.http import JsonResponse, HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO

from main.utils.logs import log_evento
from datetime import date

from main.models import Evento, Inscricao, Usuario, Certificado, Log
from .decorators import admin_required, is_admin
from main.forms.forms_usuario import RegistroCompletoForm
from main.forms.forms_evento import EventoForm

#  Landing Page
def landingPage(request):
    return render(request, 'main/landing.html')


def loginPage(request):
    if request.method == "POST":
        print("DEBUG LOGIN: entrou POST")
        print("DEBUG LOGIN: POST =", request.POST)

        email = request.POST.get("email")
        password = request.POST.get("password")
        print("DEBUG LOGIN: email =", repr(email))
        print("DEBUG LOGIN: password vazio?", password == "")

        user = authenticate(request, username=email, password=password)
        print("DEBUG LOGIN: user autenticado =", user)

        if user is None:
            messages.error(request, "E-mail ou senha inválidos.")
            return render(request, "main/login.html")

        perfil = getattr(user, "perfil", None)
        print("DEBUG LOGIN: perfil =", perfil)

        if perfil and not perfil.email_confirmado:
            print("DEBUG LOGIN: email NÃO confirmado")
            messages.warning(
                request,
                "Seu cadastro ainda não foi confirmado. Verifique seu e-mail para concluir a ativação."
            )
            return redirect("aguardar_confirmacao")

        print("DEBUG LOGIN: vai logar")
        login(request, user)

        # >>> redirecionamento condicional <<<
        if is_admin(user):
            print("DEBUG LOGIN: usuário é admin, indo para admin_dashboard")
            return redirect("admin_dashboard")   # use o name da URL do painel admin
        else:
            print("DEBUG LOGIN: usuário NÃO é admin, indo para dashboard_page")
            return redirect("dashboard_page")    # dashboard normal

    return render(request, "main/login.html")



# VIEWS DE CONFIRMAÇÃO DE EMAIL


def aguardar_confirmacao(request):
    return render(request, "main/confirmacao_email/aguardar_confirmacao.html")

def confirmacao_sucesso(request):
    return render(request, "main/confirmacao_email/confirmacao_sucesso.html")

def confirmar_email(request, token):
    try:
        # 1) Recupera o ID do usuário a partir do token
        user_id = signing.loads(
            token,
            salt='confirmacao-email-sgea',  # MESMO salt usado na registerPage
            max_age=60 * 15,          # 15 minutos de validade
        )
    except signing.BadSignature:
        # Token adulterado ou inválido
        messages.error(request, 'Link de confirmação inválido.')
        return redirect('login_page')
    except signing.SignatureExpired:
        # Token expirado (se usar max_age)
        messages.error(request, 'Link de confirmação expirado.')
        return redirect('login_page')

    # 2) Busca o perfil do usuário
    perfil = get_object_or_404(Usuario, user_id=user_id)

    # 3) Se já estava confirmado
    if perfil.email_confirmado:
        messages.info(request, 'Seu e-mail já havia sido confirmado.')
        return redirect('login_page')

    # 4) Confirma o e-mail
    perfil.email_confirmado = True
    perfil.save()

    messages.success(request, 'E-mail confirmado com sucesso!')
    return redirect('confirmacao_sucesso')



# @login_required
def logout_view(request):
    logout(request)  # Encerra a sessão do user
    return redirect('login_page')


# Render da register page
def registerPage(request):
    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST)
        if form.is_valid():
            user = form.save()

            # 1) Gera o token
            token = signing.dumps(user.pk, salt='confirmacao-email-sgea')

            # 2) Monta a URL de confirmação
            confirm_path = reverse('confirmar-email', args=[token])
            confirm_url = request.build_absolute_uri(confirm_path)

            # 3) Monta a URL absoluta da logo
            logo_path = static('main/img/logo.png')  # ajuste o caminho se necessário
            logo_url = request.build_absolute_uri(logo_path)

            # 4) Assunto do e-mail
            assunto = 'Confirmação de cadastro - Portal EnCUCA'

            # 5) Corpo em texto simples (fallback)
            mensagem_texto = (
                'Olá, {nome}.\n\n'
                'Obrigado por se cadastrar no Portal EnCUCA.\n'
                'Para ativar sua conta, acesse o link abaixo:\n'
                f'{confirm_url}\n\n'
                'Se você não realizou este cadastro, ignore este e-mail.'
            ).format(nome=user.first_name or 'usuário')

            # 6) Corpo em HTML, usando o template
            mensagem_html = render_to_string(
                'main/confirmacao_email/confirmacao_email.html',
                {
                    'nome_usuario': user.first_name or 'usuário',
                    'url_confirmacao': confirm_url,
                    'logo_url': logo_url,
                }
            )

            remetente = settings.DEFAULT_FROM_EMAIL
            destinatarios = [user.email]

            # 7) Envio do e-mail com HTML
            send_mail(
                assunto,
                mensagem_texto,           # plain text (fallback)
                remetente,
                destinatarios,
                html_message=mensagem_html  # versão HTML
            )

            return redirect('login_page')
    else:
        form = RegistroCompletoForm()

    return render(request, 'main/register.html', {'form': form})



# Render do dashboard
@login_required
def dashboardPage(request):
    return render(request, 'main/dashboard.html')


# VIEW DO PROFILE
# views.py (trecho completo da user_profile com confirmar presença)
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, password_validation
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import Usuario, Inscricao, Certificado  # ajuste se Inscricao/Certificado estiverem em outro app


def user_profile(request):
    user = request.user

    perfil, created = Usuario.objects.get_or_create(
        user=user,
        defaults={"nome_perfil": user.get_full_name() or user.username}
    )

    inscricoes = (
        Inscricao.objects
        .filter(usuario=perfil)
        .select_related("evento")
        .order_by("-data_inscricao")
    )

    certificados = (
        Certificado.objects
        .filter(inscricao__usuario=perfil)
        .select_related("inscricao", "inscricao__evento")
        .order_by("-data_emissao")
    )

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # -------- CONFIRMAR PRESENÇA (AJAX) --------
        if form_type == "confirmar_presenca":
            inscricao_id = request.POST.get("inscricao_id")

            if not inscricao_id:
                return JsonResponse({"ok": False, "error": "inscricao_id ausente."}, status=400)

            try:
                inscricao = Inscricao.objects.get(id=inscricao_id, usuario=perfil)
            except Inscricao.DoesNotExist:
                return JsonResponse({"ok": False, "error": "Inscrição não encontrada."}, status=404)

            if inscricao.presenca_confirmada:
                return JsonResponse({"ok": True, "already": True})

            inscricao.presenca_confirmada = True
            inscricao.save(update_fields=["presenca_confirmada"])
            return JsonResponse({"ok": True})

        # -------- EDITAR DADOS PESSOAIS --------
        if form_type == "editar_dados":
            nome_perfil = request.POST.get("nome_perfil", "").strip()
            telefone = request.POST.get("telefone", "").strip()
            instituicao = request.POST.get("instituicao", "").strip()

            if not nome_perfil:
                messages.error(request, "O campo Nome Perfil é obrigatório.")
            else:
                perfil.nome_perfil = nome_perfil
                perfil.telefone = telefone
                perfil.instituicao = instituicao
                perfil.save()
                messages.success(request, "Dados pessoais atualizados com sucesso.")
                return redirect("user_profile")

        # -------- ALTERAR SENHA --------
        elif form_type == "alterar_senha":
            senha_atual = request.POST.get("senha_atual", "")
            nova_senha = request.POST.get("nova_senha", "")
            confirmar_senha = request.POST.get("confirmar_senha", "")

            if not user.check_password(senha_atual):
                messages.error(request, "A senha atual informada está incorreta.")
            elif not nova_senha:
                messages.error(request, "A nova senha não pode ficar em branco.")
            elif nova_senha != confirmar_senha:
                messages.error(request, "A confirmação da senha não confere.")
            else:
                try:
                    password_validation.validate_password(nova_senha, user=user)
                except Exception as e:
                    for erro in e:
                        messages.error(request, erro)
                else:
                    user.set_password(nova_senha)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Senha alterada com sucesso.")
                    return redirect("user_profile")

    context = {
        "user": user,
        "perfil": perfil,
        "inscricoes": inscricoes,
        "certificados": certificados,
    }

    return render(request, "main/profile/profile.html", context)


# VIEW DE INSCRIÇÕES

@login_required
def subscription_page(request):
    """
    Lista as inscrições do usuário logado.
    """
    perfil = getattr(request.user, "perfil", None)

    inscricoes = (
        Inscricao.objects
        .filter(usuario=perfil)
        .select_related("evento")
        .order_by("-data_inscricao")
    ) if perfil else Inscricao.objects.none()

    context = {
        "user": request.user,
        "inscricoes": inscricoes,
    }
    return render(request, "main/subscriptions.html", context)

@login_required
def confirmar_presenca(request, inscricao_id):
    if request.method != "POST":
        raise Http404

    usuario = request.user.perfil

    inscricao = get_object_or_404(Inscricao, pk=inscricao_id, usuario=usuario)

    if not inscricao.presenca_confirmada:
        inscricao.presenca_confirmada = True
        inscricao.save(update_fields=["presenca_confirmada"])

    url = reverse("minhas_inscricoes") + "?popup=presenca_confirmada"
    return redirect(url)


@login_required
def inscrever_evento(request, evento_id):
    if request.method != "POST":
        return redirect("eventos_list")  # ajuste para sua url

    evento = get_object_or_404(Evento, pk=evento_id)
    usuario = request.user.perfil

    # Regras do seu model
    if not evento.pode_inscrever(usuario):
        url = reverse("eventos_list") + "?popup=inscricao_negada"
        return redirect(url)

    Inscricao.objects.get_or_create(evento=evento, usuario=usuario)

    # Pop-up pedindo confirmação no perfil
    url = reverse("eventos_list") + "?popup=confirmar_no_perfil"
    return redirect(url)

#  CERTIFICADO

@login_required
def certificado_detalhe(request, codigo_certificado):
    """
    Exibe um certificado pelo UUID (codigo_certificado).

    Regras:
    - Admin (superuser ou perfil ADM) pode ver qualquer certificado.
    - Usuário comum só pode ver certificado da própria inscrição.
    - Certificado é gerado automaticamente se o evento já tiver terminado.
    """

    qs = Certificado.objects.select_related(
        "inscricao__usuario",
        "inscricao__evento"
    )

    # --------------------------------------------------
    # Verifica se é admin
    # --------------------------------------------------
    is_admin = False
    if request.user.is_superuser:
        is_admin = True
    else:
        perfil = getattr(request.user, "perfil", None)
        if perfil and getattr(perfil, "tipo", None) == "ADM":
            is_admin = True

    # --------------------------------------------------
    # Busca certificado (ou inscrição relacionada)
    # --------------------------------------------------
    if is_admin:
        certificado = get_object_or_404(
            qs,
            codigo_certificado=codigo_certificado
        )
        inscricao = certificado.inscricao
    else:
        perfil = getattr(request.user, "perfil", None)
        if not perfil:
            raise Http404

        certificado = get_object_or_404(
            qs,
            codigo_certificado=codigo_certificado,
            inscricao__usuario=perfil,
        )
        inscricao = certificado.inscricao

    evento = inscricao.evento

    # --------------------------------------------------
    # Regra: evento precisa ter terminado
    # --------------------------------------------------
    if evento.data_fim > date.today():
        raise Http404  # ainda não pode emitir certificado

    # --------------------------------------------------
    # Geração automática (caso não exista)
    # --------------------------------------------------
    if not hasattr(inscricao, "certificado"):
        certificado = Certificado.objects.create(inscricao=inscricao)

        log_evento(
            usuario=request.user,
            acao="CERTIFICATE_GENERATED",
            evento=evento,
            detalhes=f"Certificado gerado automaticamente (UUID: {certificado.codigo_certificado})",
        )

    # --------------------------------------------------
    # Log de consulta
    # --------------------------------------------------
    log_evento(
        usuario=request.user,
        acao="CERTIFICATE_VIEWED",
        evento=evento,
        detalhes=f"Certificado visualizado (UUID: {certificado.codigo_certificado})",
    )

    return render(
        request,
        "main/certificado_detalhe.html",
        {"certificado": certificado},
    )


@login_required
def meus_certificados(request):
    """
    Retorna os certificados do usuário logado em JSON.
    Usado pelo modal no perfil.
    """
    perfil = getattr(request.user, "perfil", None)
    if not perfil:
        return JsonResponse([], safe=False)

    certificados = (
        Certificado.objects
        .filter(inscricao__usuario=perfil)
        .select_related("inscricao__evento")
        .order_by("-data_emissao")
    )

    data = []
    for cert in certificados:
        data.append({
            "codigo": str(cert.codigo_certificado),
            "evento": cert.inscricao.evento.titulo,
            "data_emissao": cert.data_emissao.strftime("%Y-%m-%d"),
        })

    return JsonResponse(data, safe=False)



@login_required
def certificado_pdf(request, codigo_certificado):
    """
    Gera e retorna o PDF do certificado.
    Se não existir, gera automaticamente (evento encerrado).
    """

    qs = Certificado.objects.select_related(
        "inscricao__usuario",
        "inscricao__evento"
    )

    # verifica admin
    is_admin = False
    if request.user.is_superuser:
        is_admin = True
    else:
        perfil = getattr(request.user, "perfil", None)
        if perfil and getattr(perfil, "tipo", None) == "ADM":
            is_admin = True

    if is_admin:
        certificado = get_object_or_404(qs, codigo_certificado=codigo_certificado)
        inscricao = certificado.inscricao
    else:
        perfil = getattr(request.user, "perfil", None)
        if not perfil:
            raise Http404

        certificado = get_object_or_404(
            qs,
            codigo_certificado=codigo_certificado,
            inscricao__usuario=perfil,
        )
        inscricao = certificado.inscricao

    evento = inscricao.evento

    # evento precisa ter terminado
    if evento.data_fim > date.today():
        raise Http404

    # gera automaticamente se não existir
    if not hasattr(inscricao, "certificado"):
        certificado = Certificado.objects.create(inscricao=inscricao)

        log_evento(
            usuario=request.user,
            acao="CERTIFICATE_GENERATED",
            evento=evento,
            detalhes=f"Certificado gerado automaticamente (UUID: {certificado.codigo_certificado})",
        )

    # log de download
    log_evento(
        usuario=request.user,
        acao="CERTIFICATE_DOWNLOADED",
        evento=evento,
        detalhes=f"Download do certificado (UUID: {certificado.codigo_certificado})",
    )

    # -------------------------
    # GERAÇÃO DO PDF (SIMPLES)
    # -------------------------
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(300, 750, "CERTIFICADO")

    p.setFont("Helvetica", 12)
    p.drawCentredString(
        300, 700,
        f"Certificamos que {inscricao.usuario.nome_perfil}"
    )

    p.drawCentredString(
        300, 670,
        f"participou do evento '{evento.titulo}'."
    )

    p.drawCentredString(
        300, 640,
        f"Data do evento: {evento.data_inicio} a {evento.data_fim}"
    )

    p.showPage()
    p.save()

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="certificado_{certificado.codigo_certificado}.pdf"'
    )

    return response




# --------------- RENDER DAS TELAS DE EVENTO --------------------

# TELA INICIAL (DASHBOARD)

# @login_required
def events_dashboard_page(request):
    # Lista principal (tabela)
    eventos = (
        Evento.objects
        .filter(status="Ativo")
        .order_by("data_inicio")
    )

    # Destaques do carrossel
    eventos_destaque = eventos[:3]

    context = {
        "eventos": eventos,
        "eventos_destaque": eventos_destaque,
    }
    return render(request, "main/eventos/events_dashboard.html", context)



# LISTAGEM DE TODOS OS EVENTOS

@login_required
def events_list_page(request):
    eventos = Evento.objects.select_related("organizador").all()
    context = {
        "eventos": eventos,
    }
    return render(request, "main/eventos/events_list.html", context)



# VIEW PARA DETALHE DE EVENTO

# @login_required
@login_required
def eventDetailPage(request, event_id):
    evento = get_object_or_404(Evento, pk=event_id)
    usuario = request.user.perfil  # seu model Usuario

    if request.method == "POST":
        # Tenta inscrever
        if not evento.pode_inscrever(usuario):
            messages.error(request, "Você não pode se inscrever neste evento.")
            return redirect('event_detail', event_id=evento.id)

        # Se pode inscrever, cria a inscrição
        Inscricao.objects.create(evento=evento, usuario=usuario)
        messages.success(request, "Inscrição realizada com sucesso!")
        return redirect('event_detail', event_id=evento.id)

    # Se for GET, monta as flags para o template
    contexto = {
        "evento": evento,
        "ja_inscrito": evento.usuario_ja_inscrito(usuario),
        "pode_inscrever": evento.pode_inscrever(usuario),
        "total_inscricoes": evento.total_inscricoes(),
        "tem_vagas": evento.tem_vagas(),
    }

    return render(request, 'main/events.html', contexto)



# VIEW PARA CRIAR EVENTO

@login_required
def criar_evento(request):
    # bloqueia quem não for ADM
    if not request.user.perfil.perfil_adm():
        return HttpResponseForbidden("Você não tem permissão para criar eventos.")

    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            # organizador = perfil do usuário logado
            evento.organizador = request.user.perfil
            evento.save()
            return redirect("eventos_dashboard_page")
    else:
        form = EventoForm()

    return render(request, "main/eventos/criar_evento.html", {"form": form})

