# Portal EnCUCA  
## Sistema de Gestão de Eventos Acadêmicos (SGEA)

---

## 1. Apresentação

O **Portal EnCUCA – Sistema de Gestão de Eventos Acadêmicos (SGEA)** é uma aplicação web desenvolvida para apoiar a organização, divulgação e gestão de eventos acadêmicos, como palestras, seminários, minicursos e semanas acadêmicas.

O sistema foi projetado com foco em **boas práticas de desenvolvimento backend**, segurança, organização do código e aderência aos requisitos propostos no Projeto 2 da disciplina, contemplando autenticação, regras de negócio, auditoria e integração via API REST.

---

## 2. Tecnologias Utilizadas

- **Python 3**
- **Django**
- **Django REST Framework (DRF)**
- **SQLite** (ambiente de desenvolvimento)
- HTML/CSS (camada de apresentação)
- SMTP (envio de e-mails)

---

## 3. Arquitetura do Sistema

O projeto segue o padrão **MVC/MVT** do Django, com separação clara de responsabilidades:

- **Models**: regras de negócio e persistência
- **Views**: controle das requisições web e API
- **Templates**: renderização das páginas
- **Serializers (DRF)**: transformação de dados para JSON
- **Permissions / Decorators**: controle de acesso
- **Logs**: auditoria das ações relevantes

A API REST permite integração com o frontend e futuras aplicações externas.

---

## 4. Funcionalidades Implementadas

### 4.1 Usuários
- Cadastro de usuários (Aluno, Professor, Organizador)
- Autenticação por login e senha
- Confirmação de e-mail obrigatória
- Atualização de dados cadastrais

### 4.2 Eventos
- Cadastro, edição e cancelamento de eventos
- Definição de vagas, datas, horários e responsável
- Upload e exibição de banner do evento
- Listagem e visualização de detalhes

### 4.3 Inscrições
- Inscrição em eventos via sistema e API
- Controle de vagas
- Bloqueio de inscrições duplicadas
- Cancelamento conforme regras

### 4.4 API REST
- Login com token
- Listagem de eventos
- Detalhe de evento
- Inscrição em evento
- Rate limit (throttling)

### 4.5 Auditoria
- Registro de ações críticas:
  - Eventos
  - Inscrições
  - Consultas via API
- Tela administrativa para consulta de logs

### 4.6 Certificados
- Estrutura de emissão criada
- Model, view e template configurados
- Automação de emissão prevista (em andamento)

---

## 5. Status do Projeto

✔ Funcionalidades principais implementadas  
✔ API REST funcional  
✔ Validações e regras de negócio aplicadas  
✔ Identidade visual implementada  

⏳ Emissão automática de certificados (em evolução)

---

## 6. Como Executar o Projeto

Consulte o arquivo **Guia_Instalacao.md**.

---

## 7. Documentação Complementar

- Guia de Instalação
- Guia de Testes
- Casos de Uso
- Requisitos Funcionais
- Requisitos Não Funcionais
- Documentação da API
- Arquitetura do Backend

---

## 8. Considerações Finais

O Portal EnCUCA atende aos objetivos propostos para o Projeto 2, demonstrando domínio dos conceitos de backend com Django, API REST, segurança, organização de código e regras de negócio.
