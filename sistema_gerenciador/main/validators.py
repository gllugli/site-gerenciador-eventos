from django.core.exceptions import ValidationError


class SenhaForteValidator:
    def validate(self, password, user=None):
        tem_letra, tem_numero, tem_especial = False, False, False

        # Percorre letra por letra verificando os caracteres necessários
        for c in password:
            if c.isalpha():
                tem_letra=True
            elif c.isdigit():
                tem_numero=True
            else:
                tem_especial=True


        # Se não seguir o padrão necessário, mandar essa mensagem de Erro de Validação
        if not tem_letra or not tem_numero or not tem_especial:
            raise ValidationError("A senha deve conter pelo menos uma letra, um número e um caractere especial.")

    def get_help_text(self):
        return "Sua senha deve conter pelo menos uma letra, um número e um caractere especial."
