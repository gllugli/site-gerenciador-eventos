from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.core import signing
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError  # se quiser capturar erro genérico do token
from django.http import HttpResponseForbidden

from main.models import Evento, Inscricao, Usuario
from main.forms.forms_usuario import RegistroCompletoForm
from main.forms.forms_evento import EventoForm


#  Landing Page
def landingPage(request):
    return render(request, 'main/landing.html')


# Render da página de login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login

def loginPage(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Autentica usando o e-mail como username
        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "E-mail ou senha inválidos.")
            return render(request, "main/login.html")

        # Usa o related_name='perfil'
        perfil = getattr(user, "perfil", None)

        # Se existir perfil e o e-mail NÃO estiver confirmado
        if perfil and not perfil.email_confirmado:
            messages.warning(
                request,
                "Seu cadastro ainda não foi confirmado. Verifique seu e-mail para concluir a ativação."
            )
            return redirect("aguardar_confirmacao")

        # Tudo ok: faz login e manda para o dashboard
        login(request, user)
        return redirect("dashboard_page")

    # GET -> só exibe a tela de login
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
            logo_path = static('main/img/logo_CEUB.png')  # ajuste o caminho se necessário
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
# @login_required
def dashboardPage(request):
    return render(request, 'main/dashboard.html')


# --------------- RENDER DAS TELAS DE EVENTO --------------------
# @login_required
def events_dashboard_page(request):
    eventos_destaque = (
        Evento.objects
        .filter(status="Ativo")
        .order_by("data_inicio")[:3]
    )

    context = {
        "eventos_destaque": eventos_destaque,
    }
    return render(request, 'main/eventos/events_dashboard.html', context)


def events_list_page(request):
    return render(request, 'main/events_list.html')


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

