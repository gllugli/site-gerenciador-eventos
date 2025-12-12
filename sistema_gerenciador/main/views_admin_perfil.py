# views.py
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Usuario

# Regex genéricos – ajuste se quiser um padrão diferente
EMAIL_REGEX = re.compile(r"^[\w\.\+\-]+@[A-Za-z0-9\-]+\.[A-Za-z0-9\.\-]+$")
# Min 8, 1 maiúscula, 1 minúscula, 1 dígito, 1 caractere especial
SENHA_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&\.\-_])[A-Za-z\d@$!%*?&\.\-_]{8,}$"
)


@login_required
def admin_usuarios(request):
    # LISTAGEM / BUSCA
    q = request.GET.get("q", "").strip()
    usuarios_qs = Usuario.objects.select_related("user").order_by("nome_completo")

    if q:
        usuarios_qs = usuarios_qs.filter(
            Q(nome_completo__icontains=q)
            | Q(user__email__icontains=q)
            | Q(instituicao__icontains=q)
        )

    if request.method == "POST":
        action = request.POST.get("action")

        # ---------- CRIAÇÃO ----------
        if action == "create":
            nome = request.POST.get("nome_completo", "").strip()
            email = request.POST.get("email", "").strip().lower()
            telefone = request.POST.get("telefone", "").strip()
            instituicao = request.POST.get("instituicao", "").strip()
            tipo_perfil = request.POST.get("tipo_perfil", "AL")
            senha = request.POST.get("senha", "")
            senha2 = request.POST.get("senha2", "")

            # Defesa de back-end (front já valida, aqui é só garantia)
            if not EMAIL_REGEX.match(email):
                messages.error(request, "E-mail em formato inválido.")
                return redirect("usuarios_list")

            if senha != senha2:
                messages.error(request, "As senhas não conferem.")
                return redirect("usuarios_list")

            if not SENHA_REGEX.match(senha):
                messages.error(
                    request,
                    "A senha não atende aos requisitos mínimos de segurança."
                )
                return redirect("usuarios_list")

            if User.objects.filter(username=email).exists():
                messages.error(request, "Já existe um usuário com este e-mail.")
                return redirect("usuarios_list")

            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=senha,
                    first_name=nome,
                )

                Usuario.objects.create(
                    user=user,
                    nome_completo=nome,
                    telefone=telefone,
                    instituicao=instituicao,
                    tipo_perfil=tipo_perfil,
                    email_confirmado=False,  # SEMPRE False (valida no login)
                )
                messages.success(request, "Usuário criado com sucesso.")
            except Exception as e:
                messages.error(request, f"Erro ao criar usuário: {e}")

            return redirect("usuarios_list")

        # ---------- EDIÇÃO ----------
        if action == "update":
            usuario_id = request.POST.get("usuario_id")
            usuario = get_object_or_404(Usuario, id=usuario_id)
            user = usuario.user

            nome = request.POST.get("nome_completo", "").strip()
            telefone = request.POST.get("telefone", "").strip()
            instituicao = request.POST.get("instituicao", "").strip()
            tipo_perfil = request.POST.get("tipo_perfil", "AL")
            nova_senha = request.POST.get("nova_senha", "")

            # Atualiza dados básicos
            user.first_name = nome
            user.save()

            usuario.nome_completo = nome
            usuario.telefone = telefone
            usuario.instituicao = instituicao
            usuario.tipo_perfil = tipo_perfil
            # NÃO mexe em email_confirmado aqui
            usuario.save()

            # Se o admin informou nova senha, aplica (com regex simples)
            if nova_senha:
                if not SENHA_REGEX.match(nova_senha):
                    messages.error(
                        request,
                        "A nova senha não atende aos requisitos mínimos de segurança."
                    )
                    return redirect("usuarios_list")
                user.set_password(nova_senha)
                user.save()

            messages.success(request, "Usuário atualizado com sucesso.")
            return redirect("usuarios_list")

        # ---------- EXCLUSÃO ----------
        if action == "delete":
            usuario_id = request.POST.get("usuario_id")
            usuario = get_object_or_404(Usuario, id=usuario_id)
            try:
                usuario.user.delete()  # CASCADE exclui o perfil
                messages.success(request, "Usuário excluído com sucesso.")
            except Exception as e:
                messages.error(request, f"Erro ao excluir usuário: {e}")
            return redirect("usuarios_list")

    # GET normal
    context = {
        "usuarios": usuarios_qs,
    }
    return render(request, "main/profile/admin_profile.html", context)
