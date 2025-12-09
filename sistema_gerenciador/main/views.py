from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash, password_validation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.core import signing
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError  # se quiser capturar erro genérico do token
from django.http import HttpResponseForbidden

from main.models import Evento, Inscricao, Usuario, Certificado
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
        return redirect("dashboard_page")

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
def user_profile(request):
    """
    Exibe e atualiza o perfil do usuário logado.
    - GET: mostra os dados
    - POST (form_type=editar_dados): atualiza dados pessoais
    - POST (form_type=alterar_senha): altera a senha do usuário
    """
    user = request.user

    # garante que sempre exista um perfil vinculado
    perfil, created = Usuario.objects.get_or_create(
        user=user,
        defaults={
            "nome_perfil": user.get_full_name() or user.username,
        }
    )

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # -------- EDITAR DADOS PESSOAIS --------
        if form_type == "editar_dados":
            nome_perfil = request.POST.get("nome_perfil", "").strip()
            telefone = request.POST.get("telefone", "").strip()
            instituicao = request.POST.get("instituicao", "").strip()

            # validações básicas (ajuste conforme sua regra)
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

            # verifica senha atual
            if not user.check_password(senha_atual):
                messages.error(request, "A senha atual informada está incorreta.")
            elif not nova_senha:
                messages.error(request, "A nova senha não pode ficar em branco.")
            elif nova_senha != confirmar_senha:
                messages.error(request, "A confirmação da senha não confere.")
            else:
                # valida nova senha pelos validadores do Django
                try:
                    password_validation.validate_password(nova_senha, user=user)
                except Exception as e:
                    # e é uma lista de erros; mostramos todos
                    for erro in e:
                        messages.error(request, erro)
                else:
                    user.set_password(nova_senha)
                    user.save()
                    # mantém o usuário logado após alterar a senha
                    update_session_auth_hash(request, user)
                    messages.success(request, "Senha alterada com sucesso.")
                    return redirect("user_profile")

    context = {
        "user": user,
        "perfil": perfil,
    }
    return render(request, "main/profile/profile.html", context)


# VIEW DE INSCRIÇÕES

@login_required
def subscription_page(request):
    """
    Lista as inscrições do usuário logado.
    """
    user = request.user

    # supondo que Inscricao tenha FK para User ou para Usuario
    # Exemplo 1: FK direto para User: Inscricao.user
    # inscricoes = Inscricao.objects.filter(user=user).select_related("evento")

    # Exemplo 2: FK para Usuario (perfil): Inscricao.usuario
    # e Usuario tem OneToOne com User (related_name="perfil")
    try:
        perfil = user.perfil
        inscricoes = Inscricao.objects.filter(usuario=perfil).select_related("evento")
    except Exception:
        inscricoes = Inscricao.objects.none()

    context = {
        "user": user,
        "inscricoes": inscricoes,
    }
    return render(request, "main/subscriptions.html", context)

#  CERTIFICADO

def certificado_detalhe(request, codigo_certificado):
    certificado = get_object_or_404(
        Certificado,
        codigo_certificado=codigo_certificado
    )
    context = {
        "certificado": certificado,
    }
    return render(request, "main/certificado_detalhe.html", context)



# --------------- RENDER DAS TELAS DE EVENTO --------------------

# TELA INICIAL (DASHBOARD)

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


# LISTAGEM DE TODOS OS EVENTOS

def events_list_page(request):
    return render(request, 'main/events_list.html')



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

