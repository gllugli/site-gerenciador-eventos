from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from main.api.views.evento_views import EventoListAPIView, EventoDetailAPIView

urlpatterns = [
    path('eventos/', EventoListAPIView.as_view(), name='evento-list'),
    path('eventos/<int:pk>/', EventoDetailAPIView.as_view(), name='evento-detail'),
    path('token/', obtain_auth_token, name='api-token'),
]
