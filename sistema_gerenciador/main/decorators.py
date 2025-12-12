from django.contrib.auth.decorators import user_passes_test, login_required

def is_admin(user):
    # 1) precisa estar autenticado
    if not user.is_authenticated:
        return False

    # 2) se for staff/superuser, já considera admin
    if user.is_staff or user.is_superuser:
        return True

    # 3) tenta pegar o perfil relacionado
    perfil = getattr(user, "perfil", None)
    if not perfil:
        return False

    # 4) pega o tipo de perfil ("AL", "PR", "ADM"...)
    #    ajuste o nome do campo se for diferente
    tipo = getattr(perfil, "tipo_perfil", None)
    if tipo is None:
        tipo = getattr(perfil, "perfil", None)

    return tipo == "ADM"


def admin_required(view_func):
    decorated_view_func = login_required(
        user_passes_test(is_admin)(view_func)
    )
    return decorated_view_func
