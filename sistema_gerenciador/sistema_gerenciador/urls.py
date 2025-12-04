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

urlpatterns = [    
    path('admin/', admin.site.urls),
    path('api/', include("main.api.urls")),

    # --------------- URL DAS TELAS INICIAIS ----------------------

    path('', views.loginPage, name="landing_page"),
    path('login/', views.loginPage, name="login_page"),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.registerPage, name="register_page"),
    path('dashboard/', views.dashboardPage, name="dashboard_page"),

    # --------------- URL DAS TELAS DE EVENTO ---------------------

    path('events/', views.events_dashboard_page, name="event_dashboard"),  # PESQUISA FEITA VIA URL API
    path('events/list', views.events_list_page, name="events_list"),
    path('eventos/<int:event_id>/', views.eventDetailPage, name='event_detail'),
    path('eventos/<int:pk>/inscrever/', EventoInscricaoAPIView.as_view(), name='evento_inscrever'),

    # --------------- URL DAS TELAS DE PERFIL ---------------------

    path('profile/', views.profile_view, name="user_profile"),

    # --------------- URL DAS TELAS DE INSCRIÇÃO ------------------

    path('subscription/', views.subscription_view, name="subscription_page"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
        )
