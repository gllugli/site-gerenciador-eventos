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

from main import views

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
    path('events/', views.allEventsPage, name="all_events"),
    path('event/detail/<int:pk>', views.eventDetailPage, name="event"),

    path('event/admin/create_event', views.adminCreateEventPage, name="admin_create_event"),
    path('event/admin/event_detail/<int:pk>', views.adminEventDetailPage, name="admin_event_detail"),
    path('event/admin/update_event/<int:pk>', views.adminUpdateEventDetailPage, name="admin_update_event"),
    path('event/admin/delete_event/<int:pk>', views.adminDeleteUserPage, name="admin_delete_event"),

    # --------------- URL DAS TELAS DE PERFIL ---------------------
    path('profile/', views.showUserProfilePage, name="user_profile"),

    path('profile/admin/register_user', views.adminCreateUserPage, name="admin_create_user"),
    path('profile/admin/update_user/<int:pk>', views.adminUpdateUserDetailPage, name="admin_update_user"),
    path('profile/admin/delete_user/<int:pk>', views.adminDeleteUserPage, name="admin_delete_user"),

    # --------------- URL DAS TELAS DE INSCRIÇÃO ------------------
    path('subscription/', views.showUserSubscriptionPage, name="subscription_page"),

    path('subscription/admin', views.adminDeleteUserSubscriptionPage, name="admin_delete_user_subscription"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
        )
