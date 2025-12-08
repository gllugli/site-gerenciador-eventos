"""
URL configuration for sistema_gerenciador project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.authtoken.views import obtain_auth_token

from main import views
from main.api.views.evento_views import EventoInscricaoAPIView
from main.views import confirmar_email

urlpatterns = [


    #  EXTRAS

    path('admin/', admin.site.urls),

    path('api/', include("main.api.urls")),


    #  TELAS INICIAS (LOGIN, LOGOUT, CADASTRO, CONFIRMAÇÃO DE EMAIL)

    path('', views.landingPage, name="landing_page"),

    path('login/', views.loginPage, name="login_page"),

    path(
        'aguardar-confirmacao/', views.aguardar_confirmacao, name='aguardar_confirmacao'
    ),

    path(
        'confirmacao-sucesso/',
        views.confirmacao_sucesso,
        name='confirmacao_sucesso'
    ),

    path('logout/', views.logout_view, name='logout'),

    path('register/', views.registerPage, name="register_page"),

    path('confirmar-email/<str:token>/', confirmar_email, name='confirmar-email'),


    #  TELAS INTERNAS APLICAÇÃO

    path('dashboard/', views.dashboardPage, name="dashboard_page"),

    
    # EVENTOS

    path('events/', views.events_dashboard_page, name="event_dashboard"),  

    path('events/list', views.events_list_page, name="events_list"),

    path('eventos/<int:event_id>/', views.eventDetailPage, name='event_detail'), 

    path('eventos/<int:pk>/inscrever/', EventoInscricaoAPIView.as_view(), name='evento_inscrever'),

    path("eventos/novo/", views.criar_evento, name="criar_evento"),



    # path('profile/', views.profile_view, name="user_profile"),

    # path('subscription/', views.subscription_view, name="subscription_page"),

    # path('admin/events/', views.admin_events_view, name='admin-events'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
        )
