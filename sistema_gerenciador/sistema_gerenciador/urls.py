from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from main import views
from main import views_admin_eventos
from main.api.views.evento_views import EventoInscricaoAPIView
from main.views import confirmar_email
from main.views_admin_inscricoes import InscricaoListView
from main import views_admin_perfil

urlpatterns = [
    # ========== ÁREA ADMIN DA APLICAÇÃO ==========
    path("painel-admin/", views_admin_eventos.admin_dashboard, name="admin_dashboard"),

    # Lista administrativa de eventos
    path(
        "painel-admin/eventos/",
        views_admin_eventos.admin_event_list,
        name="admin_event_list",
    ),

    # Detalhes administrativos de um evento
    path(
        "painel-admin/eventos/<int:pk>/",
        views_admin_eventos.admin_event_detail,
        name="admin_event_detail",
    ),

    # Criar novo evento (admin)
    path(
        "painel-admin/eventos/novo/",
        views_admin_eventos.event_create,
        name="event_create",
    ),

    # Editar evento (admin)
    path(
        "painel-admin/eventos/<int:pk>/editar/",
        views_admin_eventos.event_update,
        name="event_update",
    ),

    # Deletar evento (admin)
    path(
        "painel-admin/eventos/<int:pk>/deletar/",
        views_admin_eventos.event_delete,
        name="event_delete",
    ),

    path('inscricoes/', InscricaoListView.as_view(), name='inscricao_list'),

    path(
        "painel-admin/usuarios/",
        views_admin_perfil.admin_usuarios,
        name="usuarios_list",
    ),
    
    # ========== DJANGO ADMIN ==========
    path("admin/", admin.site.urls),

    # ========== API ==========
    path("api/", include("main.api.urls")),

    # ========== TELAS INICIAIS ==========
    path("", views.landingPage, name="landing_page"),
    path("login/", views.loginPage, name="login_page"),
    path("aguardar-confirmacao/", views.aguardar_confirmacao, name="aguardar_confirmacao"),
    path("confirmacao-sucesso/", views.confirmacao_sucesso, name="confirmacao_sucesso"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.registerPage, name="register_page"),
    path("confirmar-email/<str:token>/", confirmar_email, name="confirmar-email"),

    # ========== TELAS INTERNAS ==========
    path("dashboard/", views.dashboardPage, name="dashboard_page"),

    # EVENTOS (usuário)
    path("events/", views.events_dashboard_page, name="event_dashboard"),
    path("events/list/", views.events_list_page, name="events_list"),
    path("eventos/<int:event_id>/", views.eventDetailPage, name="event_detail"),
    path("eventos/<int:pk>/inscrever/", EventoInscricaoAPIView.as_view(), name="evento_inscrever"),
    path("eventos/novo/", views.criar_evento, name="criar_evento"),

    # CERTIFICADO
    path("certificados/meus/", views.meus_certificados, name="meus_certificados"),
    path(
        "certificados/<uuid:codigo_certificado>/pdf/",
        views.certificado_pdf,
        name="certificado_pdf"
    ),

    path("perfil/inscricoes/", views.subscription_page, name="subscription_page"),
    path("perfil/inscricoes/<int:inscricao_id>/confirmar/", views.confirmar_presenca, name="confirmar_presenca"),

    path("profile/", views.user_profile, name="user_profile"),
    path("inscricoes/", views.subscription_page, name="subscription_page"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
