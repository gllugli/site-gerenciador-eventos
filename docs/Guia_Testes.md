# Guia de Testes - Sistema de Gerenciamento de Eventos (SGEA)

Este guia descreve os procedimentos de teste para o Sistema de Gerenciamento de Eventos (SGEA), garantindo a qualidade e a estabilidade da aplicação.

## 1. Tipos de Testes

O projeto SGEA utiliza uma abordagem de testes em várias camadas para garantir que todos os componentes do sistema funcionem corretamente.

### 1.1. Testes Unitários

**Objetivo:** Verificar o funcionamento de pequenas partes isoladas do código, como funções, métodos e classes.

**Ferramentas:**
*   **Django Test Framework:** Framework de testes padrão do Django, baseado no `unittest` do Python.

**Localização dos Testes:**
Os testes unitários estão localizados no arquivo `main/tests.py` de cada aplicação Django.

**Como Executar:**
1.  Abra o terminal na pasta raiz do projeto (`sistema_gerenciador`).
2.  Ative o ambiente virtual, se estiver usando um.
3.  Execute o seguinte comando:

    ```bash
    python manage.py test main
    ```

    Este comando descobrirá e executará todos os testes na aplicação `main`.

**Exemplo de Teste Unitário (a ser adicionado em `main/tests.py`):**

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Evento

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        """Testa a criação de um novo usuário."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))

class EventoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='organizador', password='password')

    def test_create_evento(self):
        """Testa a criação de um novo evento."""
        evento = Evento.objects.create(
            nome_evento='Conferência de Tecnologia',
            organizador=self.user,
            local='Centro de Convenções',
            data_inicio='2025-12-25T10:00:00Z',
            data_fim='2025-12-25T18:00:00Z',
            quantidade_vagas=100
        )
        self.assertEqual(evento.nome_evento, 'Conferência de Tecnologia')
        self.assertEqual(evento.organizador.username, 'organizador')
```

### 1.2. Testes de Integração

**Objetivo:** Verificar a interação entre diferentes partes do sistema, como a comunicação entre views, models e o banco de dados.

**Ferramentas:**
*   **Django Test Client:** Permite simular requisições HTTP (GET, POST, etc.) para as views e verificar as respostas.

**Como Executar:**
Os testes de integração são executados juntamente com os testes unitários usando o mesmo comando:

```bash
python manage.py test main
```

**Exemplo de Teste de Integração (a ser adicionado em `main/tests.py`):**

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ViewsIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_dashboard_view(self):
        """Testa se a view do dashboard renderiza corretamente para um usuário logado."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/dashboard.html')
```

### 1.3. Testes de API

**Objetivo:** Garantir que os endpoints da API RESTful estejam funcionando conforme o esperado, validando requisições, respostas e códigos de status.

**Ferramentas:**
*   **Django REST Framework Test Tools:** Ferramentas específicas para testar APIs construídas com DRF.
*   **Postman / Insomnia:** Ferramentas manuais para testar os endpoints da API.

**Como Executar (Automatizado):**
Os testes automatizados da API também são executados com o comando de teste do Django.

```bash
python manage.py test main
```

**Exemplo de Teste de API (a ser adicionado em `main/tests.py`):**

```python
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Evento
from django.contrib.auth import get_user_model

User = get_user_model()

class EventoAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='password')
        self.client.force_authenticate(user=self.user)
        self.evento = Evento.objects.create(
            nome_evento='API Test Event',
            organizador=self.user,
            local='Online',
            data_inicio='2025-12-28T10:00:00Z',
            data_fim='2025-12-28T11:00:00Z',
            quantidade_vagas=50
        )

    def test_get_eventos_list(self):
        """Garante que podemos listar os eventos via API."""
        url = reverse('evento-list') # Adapte para o nome da sua URL de listagem de eventos da API
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome_evento'], 'API Test Event')

```

## 2. Testes Manuais (End-to-End)

**Objetivo:** Simular o fluxo de um usuário real para validar a experiência completa do sistema, desde o login até a inscrição em um evento.

**Cenários de Teste:**

1.  **Registro de Novo Usuário:**
    *   Acessar a página de registro.
    *   Preencher o formulário com dados válidos.
    *   Verificar se o usuário é criado e redirecionado para a página de login ou dashboard.
    *   Tentar registrar com um e-mail já existente e verificar a mensagem de erro.

2.  **Login e Autenticação:**
    *   Acessar a página de login.
    *   Tentar fazer login com credenciais inválidas e verificar a mensagem de erro.
    *   Fazer login com credenciais válidas e verificar o redirecionamento para o dashboard.

3.  **Criação de Evento (Perfil de Administrador/Organizador):**
    *   Fazer login com um usuário administrador.
    *   Navegar até a área de criação de eventos.
    *   Preencher o formulário de novo evento com dados válidos.
    *   Verificar se o evento é criado e listado corretamente.
    *   Tentar criar um evento com dados inválidos (ex: data de fim anterior à de início) e verificar as mensagens de erro.

4.  **Inscrição em um Evento (Perfil de Participante):**
    *   Fazer login com um usuário comum.
    *   Navegar pela lista de eventos disponíveis.
    *   Selecionar um evento e clicar para se inscrever.
    *   Verificar se a inscrição é confirmada e se o evento aparece na lista de "Minhas Inscrições".
    *   Tentar se inscrever no mesmo evento novamente e verificar o comportamento do sistema.

5.  **Visualização de Certificado:**
    *   Após participar de um evento, acessar a área de certificados.
    *   Verificar se o certificado está disponível para visualização ou download.

## 3. Conclusão

A combinação de testes automatizados (unitários, integração, API) e testes manuais (end-to-end) é crucial para manter a alta qualidade do SGEA. É recomendado que novos recursos sejam sempre acompanhados de seus respectivos testes automatizados.
