from django.urls import path

from main.api.views.evento_views import EventoListAPIView, EventoDetailAPIView

urlpatterns = [
    path('eventos/', EventoListAPIView.as_view(), name='evento-list'),
    path('eventos/<int:pk>/', EventoDetailAPIView.as_view(), name='evento-detail'),
]
