# main/decorators.py
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import redirect

def is_admin(user):
    # Ajuste essa lógica para o que você já tem:
    # Exemplo 1: se seu User tem perfil com método is_admin()
    perfil = getattr(user, "perfil", None)
    if not perfil:
        return False
    return getattr(perfil, "is_admin", lambda: False)()

    # Exemplo 2: se o campo no model Usuario é algo como perfil='ADM'
    # return perfil.perfil == "ADM"


def admin_required(view_func):
    """
    Restringe o acesso apenas para usuários com perfil ADM.
    """
    decorated_view_func = login_required(
        user_passes_test(
            is_admin,
            # se quiser, pode redirecionar para uma página de 'acesso negado'
            # redirect_field_name=None
        )(view_func)
    )
    return decorated_view_func
