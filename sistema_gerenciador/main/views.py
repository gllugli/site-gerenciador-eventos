from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
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
    return render(request, 'main/register.html')


# Render do dashboard
# @login_required
def dashboardPage(request):
    return render(request, 'main/dashboard.html')


# --------------- RENDER DAS TELAS DE EVENTO --------------------
# @login_required
def allEventsPage(request):
    return render(request, 'main/events.html')


# @login_required
def eventDetailPage(request): # <---- Falta ser criada
    render(request, ...)


# --------------- RENDER TELAS ADMIN ----------------------------

# @login_required
def adminCreateEventPage(request): # <---- Falta ser criada
    render(request, ...)


# @login_required
def adminEventDetailPage(request): # <---- Falta ser criada
    render(request, ...)    


# @login_required
def adminUpdateEventDetailPage(request): # <---- Falta ser criada
    render(request, ...)


# @login_required
def adminDeleteEventPage(request): # <---- Falta ser criada
    render(request, ...)


# --------------- RENDER DAS TELAS DE PERFIL --------------------

# @login_required
def showUserProfilePage(request):
    render(request, 'main/profile.html')


# --------------- RENDER TELAS ADMIN ----------------------------

# @login_required
def adminCreateUserPage(request):
    render(request, ...)


# @login_required
def adminUpdateUserDetailPage(request):
    render(request, ...)


# @login_required
def adminDeleteUserPage(request):
    render(request, ...)


# --------------- RENDER DAS TELAS DE INCRIÇÃO --------------------

# @login_required
def showUserSubscriptionPage(request):
    render(request, ...)


# --------------- RENDER TELAS ADMIN ----------------------------

# @login_required
def adminDeleteUserSubscriptionPage(request):
    render(request, ...)
