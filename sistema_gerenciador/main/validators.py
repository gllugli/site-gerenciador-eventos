from django.core.exceptions import ValidationError


class SenhaForteValidator:
    def validate(self, password, user=None):
        # 1) Inicializar três flags:
        tem_letra, tem_numero, tem_especial = False, False, False

        for c in password:
            pass

        # 2) Percorrer cada caractere da senha (for c in password:)
        #    - Se c.isalpha(): marcar que tem_letra = True
        #    - Se c.isdigit(): marcar que tem_numero = True
        #    - Se NÃO for letra nem número: marcar que tem_especial = True

        # 3) Depois do loop, verificar as três flags:
        #    Se alguma delas for False, levantar ValidationError
        #    com uma mensagem tipo:
        #      "A senha deve conter pelo menos uma letra, um número e um caractere especial."

        #    Dica: use a classe ValidationError importada acima.

        # OBS: Não retorne nada se estiver tudo certo.
        pass

    def get_help_text(self):
        # Retornar uma string com o texto de ajuda
        # Algo como: "Sua senha deve conter pelo menos uma letra, um número e um caractere especial."
        pass
