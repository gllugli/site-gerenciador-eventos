from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.shortcuts import redirect

from .models import Inscricao
from .forms.inscricao_update_forms import InscricaoUpdateForm  # ou onde você criou o form
from .utils.logs import log_evento



class InscricaoListView(LoginRequiredMixin, ListView):
    model = Inscricao
    template_name = "main/inscricao/inscricao_list.html"
    context_object_name = "inscricoes"
    paginate_by = 20

    def get_queryset(self):
        return (
            Inscricao.objects
            .select_related("evento", "usuario")
            .order_by("-data_inscricao")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_update"] = InscricaoUpdateForm()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        inscricao_id = request.POST.get("inscricao_id")

        if not action or not inscricao_id:
            messages.error(request, "Requisição inválida.")
            return redirect("inscricao_list")

        try:
            inscricao = (
                Inscricao.objects
                .select_related("evento", "usuario")
                .get(pk=inscricao_id)
            )
        except Inscricao.DoesNotExist:
            messages.error(request, "Inscrição não encontrada.")
            return redirect("inscricao_list")

        # === UPDATE ===
        if action == "update":
            form = InscricaoUpdateForm(request.POST, instance=inscricao)
            if form.is_valid():
                evento_antigo = inscricao.evento
                inscricao = form.save()

                # LOG no mesmo padrão dos eventos
                log_evento(
                    usuario=request.user,
                    acao="INSCRICAO_UPDATE",
                    evento=inscricao.evento,
                    detalhes=(
                        f"Inscrição ID {inscricao.pk} atualizada via painel admin. "
                        f"Evento: '{evento_antigo}' → '{inscricao.evento}'. "
                        f"Usuário inscrito: {inscricao.usuario}."
                    ),
                )

                messages.success(request, "Inscrição atualizada com sucesso.")
            else:
                messages.error(request, "Erro ao atualizar a inscrição.")
            return redirect("inscricao_list")

        # === DELETE ===
        if action == "delete":
            # guarda dados antes de deletar
            evento = inscricao.evento
            usuario_inscrito = inscricao.usuario
            pk_inscricao = inscricao.pk

            # LOG no mesmo padrão
            log_evento(
                usuario=request.user,
                acao="INSCRICAO_DELETE",
                evento=evento,
                detalhes=(
                    f"Inscrição ID {pk_inscricao} para o usuário "
                    f"{usuario_inscrito} no evento '{evento}' deletada via painel admin."
                ),
            )

            inscricao.delete()
            messages.success(request, "Inscrição excluída com sucesso.")
            return redirect("inscricao_list")

        messages.error(request, "Ação inválida.")
        return redirect("inscricao_list")
