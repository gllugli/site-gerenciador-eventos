from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Views (páginas)
from main import views
from main.views import confirmar_email

# Views (admin da aplicação)
from main import views_admin_eventos
from main import views_admin_perfil
from main.views_admin_inscricoes import InscricaoListView

# API
from main.api.views.evento_views import EventoInscricaoAPIView


urlpatterns = [
    # =========================================================================
    # DJANGO ADMIN (admin padrão do Django)
    # =========================================================================
    path("admin/", admin.site.urls),

    # =========================================================================
    # ÁREA ADMINISTRATIVA DA APLICAÇÃO (Painel do Organizador/Admin do sistema)
    # =========================================================================
    # Dashboard / Logs / visão geral
    path("painel-admin/", views_admin_eventos.admin_dashboard, name="admin_dashboard"),

    # Eventos (CRUD)
    path("painel-admin/eventos/", views_admin_eventos.admin_event_list, name="admin_event_list"),
    path("painel-admin/eventos/novo/", views_admin_eventos.event_create, name="event_create"),
    path("painel-admin/eventos/<int:pk>/", views_admin_eventos.admin_event_detail, name="admin_event_detail"),
    path("painel-admin/eventos/<int:pk>/editar/", views_admin_eventos.event_update, name="event_update"),
    path("painel-admin/eventos/<int:pk>/deletar/", views_admin_eventos.event_delete, name="event_delete"),

    # Usuários (admin da aplicação)
    path("painel-admin/usuarios/", views_admin_perfil.admin_usuarios, name="usuarios_list"),

    # Inscrições (admin)
    path("painel-admin/inscricoes/", InscricaoListView.as_view(), name="inscricao_list"),

    # =========================================================================
    # API (REST)
    # =========================================================================
    path("api/", include("main.api.urls")),

    # (Opcional) endpoint pontual fora do include — mantenha aqui se precisar
    path("eventos/<int:pk>/inscrever/", EventoInscricaoAPIView.as_view(), name="evento_inscrever"),

    # =========================================================================
    # AUTENTICAÇÃO / ONBOARDING
    # =========================================================================
    path("", views.landingPage, name="landing_page"),
    path("login/", views.loginPage, name="login_page"),
    path("logout/", views.logout_view, name="logout"),
    path("cadastro/", views.registerPage, name="register_page"),

    # Confirmação de e-mail
    path("aguardar-confirmacao/", views.aguardar_confirmacao, name="aguardar_confirmacao"),
    path("confirmacao-sucesso/", views.confirmacao_sucesso, name="confirmacao_sucesso"),
    path("confirmar-email/<str:token>/", confirmar_email, name="confirmar_email"),

    # =========================================================================
    # TELAS INTERNAS (usuário autenticado)
    # =========================================================================
    # Dashboard inicial
    path("dashboard/", views.dashboardPage, name="dashboard_page"),

    # Eventos (usuário)
    path("eventos/", views.events_dashboard_page, name="event_dashboard"),
    # path("eventos/list/", views.events_list_page, name="events_list"),
    # path("eventos/<int:event_id>/", views.eventDetailPage, name="event_detail"),
    # path("eventos/novo/", views.criar_evento, name="criar_evento"),

    # Perfil / Inscrições (usuário)
    path("perfil/", views.user_profile, name="user_profile"),
    path("perfil/inscricoes/", views.subscription_page, name="subscription_page"),
    path("perfil/inscricoes/<int:inscricao_id>/confirmar/", views.confirmar_presenca, name="confirmar_presenca"),

    # Certificados
    path("certificados/meus/", views.meus_certificados, name="meus_certificados"),
    path("certificados/<uuid:codigo_certificado>/pdf/", views.certificado_pdf, name="certificado_pdf"),
]

# =========================================================================
# MEDIA (somente em desenvolvimento)
# =========================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
