# Portal EnCUCA
## Sistema de Gestão de Eventos Acadêmicos (SGEA)

**Projeto acadêmico – Programação para Web**
Data da documentação: 12/12/2025

---

## 1. Apresentação

O **Portal EnCUCA – Sistema de Gestão de Eventos Acadêmicos (SGEA)** é uma aplicação web desenvolvida para apoiar a organização, divulgação e gestão de eventos acadêmicos, como palestras, seminários, minicursos e semanas acadêmicas.

O sistema foi projetado com foco em boas práticas de desenvolvimento backend, utilizando Django, com ênfase em segurança, organização do código e aderência aos requisitos propostos, contemplando autenticação, regras de negócio, auditoria e uma API REST para integrações.

---

## 2. Tecnologias Utilizadas

- **Backend**: Python 3, Django, Django REST Framework (DRF)
- **Banco de Dados**: SQLite (para ambiente de desenvolvimento)
- **Frontend**: HTML, CSS, JavaScript (renderizados via templates do Django)
- **Autenticação**: Baseada em sessão e Token (para a API)
- **E-mail**: SMTP (simulado via console no desenvolvimento)

---

## 3. Arquitetura do Sistema

O projeto segue o padrão **MVT (Model-View-Template)** do Django, com uma separação clara de responsabilidades:

- **Models**: Definição das entidades (`Usuario`, `Evento`, `Inscricao`, `Log`, `Certificado`), regras de negócio e persistência de dados.
- **Views**: Lógica de controle para requisições web e endpoints da API, gerenciando o fluxo de dados entre os models e os templates/serializers.
- **Templates**: Camada de apresentação (HTML) renderizada pelo Django, com estrutura para páginas de login, dashboard, gestão de eventos, etc.
- **Forms**: Validação e manipulação de dados de formulários, como em [`RegistroCompletoForm`](sistema_gerenciador/main/forms/forms_usuario.py).
- **Serializers (DRF)**: Transformação dos models em JSON para a API REST.
- **Decorators/Permissions**: Controle de acesso a views restritas, como [`@admin_required`](sistema_gerenciador/main/decorators.py).
- **Logs**: Auditoria de ações relevantes no sistema, armazenadas no model [`Log`](sistema_gerenciador/main/models.py).

---

## 4. Funcionalidades Implementadas

### 4.1 Usuários
- Cadastro de usuários com perfis (Aluno, Professor, Administrador).
- Autenticação por e-mail e senha.
- Confirmação de cadastro por e-mail.
- Painel administrativo para gestão de usuários ([`admin_usuarios`](sistema_gerenciador/main/views_admin_perfil.py)).
- Atualização de dados cadastrais pelo próprio usuário.

### 4.2 Eventos
- CRUD completo de eventos para administradores.
- Definição de vagas, datas, horários, localização e organizador.
- Upload e exibição de banner do evento.
- Dashboard de eventos para os usuários visualizarem e se inscreverem.

### 4.3 Inscrições
- Inscrição em eventos via sistema.
- Controle de vagas e bloqueio de inscrições duplicadas.
- Confirmação de presença pelo usuário.
- Cancelamento de inscrição (conforme regras a serem definidas).

### 4.4 API REST
- Autenticação via Token.
- Endpoints para listagem e detalhe de eventos.
- Endpoint para inscrição em eventos.
- Proteção contra uso excessivo com *rate limit* (throttling).

### 4.5 Auditoria
- Registro de ações críticas como criação de usuários, manipulação de eventos e inscrições.
- Tela administrativa para consulta de logs ([`admin_dashboard`](sistema_gerenciador/main/templates/main/admin/admin_dashboard.html)).

### 4.6 Certificados
- Geração de certificados em PDF para participantes com presença confirmada.
- Comando de gerenciamento ([`emitir_certificados`](sistema_gerenciador/main/management/commands/emitir_certificados.py)) para automatizar a emissão.

---

## 5. Status do Projeto

✔ Funcionalidades principais implementadas  
✔ API REST funcional  
✔ Validações e regras de negócio aplicadas  
✔ Identidade visual implementada  
✔ Sistema de logs e auditoria funcional

⏳ Emissão automática de certificados (em evolução)

---

## 6. Como Executar o Projeto

Consulte o arquivo [`docs/Guia_Instalacao.md`](docs/Guia_Instalacao.md).

Para popular o banco de dados com dados de teste, utilize o comando:
````sh
python manage.py seed_sgea
