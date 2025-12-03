from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout

from main.models import Evento, Inscricao, Usuario
from main.forms.forms_usuario import RegistroCompletoForm
# Create your views here.

# --------------- RENDERS TEMPORÁRIAS ---------------------------

# TEMPORÁRIA
def profile_view(request):
    return render(request, 'main/profile.html')

# TEMPORÁRIA
def subscription_view(request):
    return render(request, 'main/subscriptions.html')


# --------------- RENDER DAS TELAS INICIAIS ---------------------

def landingPage(request):  # <---- Falta ser criada
    ...


# Render da página de login
def loginPage(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        return redirect('dashboard_page')
    
    return render(request, 'main/login.html')


# @login_required
def logout_view(request):
    logout(request)  # Encerra a sessão do user
    return redirect('login_page')


# Render da register page
def registerPage(request):
    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # ou outra rota
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
    return render(request, 'main/events_dashboard.html')


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


# --------------- RENDER TELAS ADMIN ----------------------------

# @login_required
def adminCreateEventPage(request): # <---- Falta ser criada
    return render(request, ...)


# @login_required
def adminEventDetailPage(request): # <---- Falta ser criada
    return render(request, ...)    


# @login_required
def adminUpdateEventDetailPage(request): # <---- Falta ser criada
    return render(request, ...)


# @login_required
def adminDeleteEventPage(request): # <---- Falta ser criada
    return render(request, ...)


# --------------- RENDER DAS TELAS DE PERFIL --------------------

# @login_required
def showUserProfilePage(request):
    return render(request, 'main/profile.html')


# --------------- RENDER TELAS ADMIN ----------------------------

# @login_required
def adminCreateUserPage(request):
    return render(request, ...)


# @login_required
def adminUpdateUserDetailPage(request):
    return render(request, ...)


# @login_required
def adminDeleteUserPage(request):
    return render(request, ...)


# --------------- RENDER DAS TELAS DE INCRIÇÃO --------------------

# @login_required
def showUserSubscriptionPage(request):
    return render(request, ...)


# --------------- RENDER TELAS ADMIN ----------------------------

# @login_required
def adminDeleteUserSubscriptionPage(request):
    return render(request, ...)
