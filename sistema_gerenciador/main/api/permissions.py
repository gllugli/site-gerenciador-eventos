from rest_framework import permissions


class IsEmailConfirmed(permissions.BasePermission):
    """
    Permite acesso apenas a usuários com e-mail confirmado.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        perfil = getattr(request.user, 'perfil', None)

        if perfil is None:
            return False
        
        return perfil.email_confirmado
